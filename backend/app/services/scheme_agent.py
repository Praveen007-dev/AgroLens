import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Literal
from urllib.parse import urljoin, urlsplit

import httpx

from backend.app.schemas.scheme_agent import (
    SchemeDiscoveryResponse,
    SchemeCandidate,
    SchemeSourceLink,
    SchemeSourceResult,
)


AGENT_NAME = "AgroLens deterministic schemes source agent"
REQUEST_TIMEOUT_SECONDS = 8.0
MAX_RESPONSE_BYTES = 1_000_000
CACHE_TTL_SECONDS = 900
MAX_HEADING_COUNT = 12
MAX_LINK_COUNT = 8
MAX_SCHEME_CANDIDATES = 500
RELEVANT_TERMS = (
    "scheme",
    "subsid",
    "योजना",
    "ಯೋಜನೆ",
    "திட்டம்",
    "പദ്ധതി",
    "పథకం",
    "ਯੋਜਨਾ",
)
ERROR_PAGE_TERMS = (
    "something went wrong",
    "access denied",
    "temporarily unavailable",
    "page not found",
)

SOURCES = (
    {
        "source_id": "myscheme-central",
        "source_name": "myScheme — Government of India scheme discovery",
        "government_level": "central",
        "state": None,
        "source_url": "https://www.myscheme.gov.in/",
    },
    {
        "source_id": "karnataka-agriculture",
        "source_name": "Karnataka Agriculture Department",
        "government_level": "state",
        "state": "Karnataka",
        "source_url": "https://agriculture.karnataka.gov.in/",
    },
    {
        "source_id": "tamil-nadu-agriculture-schemes",
        "source_name": "Tamil Nadu Agriculture Schemes",
        "government_level": "state",
        "state": "Tamil Nadu",
        "source_url": "https://www.tnagrisnet.tn.gov.in/home/schemes/en",
    },
    {
        "source_id": "kerala-agriculture-schemes",
        "source_name": "Kerala Agriculture Department Schemes",
        "government_level": "state",
        "state": "Kerala",
        "source_url": "https://keralaagriculture.gov.in/en/schemes/",
    },
    {
        "source_id": "andhra-pradesh-agriculture",
        "source_name": "Andhra Pradesh Agriculture Department",
        "government_level": "state",
        "state": "Andhra Pradesh",
        "source_url": "https://agriculture.ap.gov.in/",
    },
    {
        "source_id": "punjab-agriculture",
        "source_name": "Punjab Agriculture Department",
        "government_level": "state",
        "state": "Punjab",
        "source_url": "https://agri.punjab.gov.in/",
    },
)
TAMIL_NADU_SCHEME_ENDPOINT = (
    "https://www.tnagrisnet.tn.gov.in/Scheme_master/getSchemesYear/"
)
TAMIL_NADU_DEPARTMENTS = (
    ("A", "Agriculture"),
    ("H", "Horticulture"),
    ("E", "Agricultural Engineering"),
    ("M", "Agri Marketing & Agri Business"),
)

_cache: tuple[float, SchemeDiscoveryResponse] | None = None
_cache_lock = threading.Lock()


class _PageMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: list[str] = []
        self.headings: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._active_capture: str | None = None
        self._active_href: str | None = None
        self._active_text: list[str] = []
        self._in_head_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attributes = dict(attrs)
        if tag == "title":
            self._in_head_title = True
        elif tag in {"h1", "h2", "h3"}:
            self._active_capture = "heading"
            self._active_text = []
        elif tag == "a":
            self._active_capture = "link"
            self._active_href = attributes.get("href")
            self._active_text = []

    def handle_data(self, data: str):
        if self._in_head_title:
            self.title.append(data)
        if self._active_capture is not None:
            self._active_text.append(data)

    def handle_endtag(self, tag: str):
        if tag == "title":
            self._in_head_title = False
        if self._active_capture == "heading" and tag in {"h1", "h2", "h3"}:
            text = " ".join(" ".join(self._active_text).split())
            if text and text not in self.headings:
                self.headings.append(text)
            self._active_capture = None
        elif self._active_capture == "link" and tag == "a":
            text = " ".join(" ".join(self._active_text).split())
            if text and self._active_href:
                self.links.append((text, self._active_href))
            self._active_capture = None
            self._active_href = None


def _is_relevant(text: str) -> bool:
    normalized = text.casefold()
    return any(term in normalized for term in RELEVANT_TERMS)


def _collect_tamil_nadu_candidates(
) -> tuple[list[SchemeCandidate], str]:
    candidates = []
    failed_departments = 0
    for department_code, department_name in TAMIL_NADU_DEPARTMENTS:
        try:
            response = httpx.post(
                TAMIL_NADU_SCHEME_ENDPOINT + department_code,
                content="",
                timeout=REQUEST_TIMEOUT_SECONDS,
                follow_redirects=False,
                headers={"User-Agent": "AgroLens source discovery/1.0"},
            )
        except httpx.RequestError:
            failed_departments += 1
            continue

        if response.is_error or 300 <= response.status_code < 400:
            failed_departments += 1
            continue
        if len(response.content) > MAX_RESPONSE_BYTES:
            failed_departments += 1
            continue
        try:
            records = response.json()
        except ValueError:
            failed_departments += 1
            continue
        if not isinstance(records, list) or len(records) > MAX_SCHEME_CANDIDATES:
            failed_departments += 1
            continue

        for record in records:
            if not isinstance(record, dict):
                failed_departments += 1
                continue
            source_record_id = record.get("scheme_id")
            name = record.get("Scheme_Name")
            if not isinstance(source_record_id, (str, int)) or not isinstance(
                name, str
            ):
                failed_departments += 1
                continue
            name = name.strip()
            if not name:
                failed_departments += 1
                continue
            local_name = record.get("Scheme_Name_Tamil")
            candidates.append(
                SchemeCandidate(
                    source_record_id=str(source_record_id),
                    department=department_name,
                    name=name,
                    local_name=(
                        local_name.strip()
                        if isinstance(local_name, str) and local_name.strip()
                        else None
                    ),
                )
            )
            if len(candidates) >= MAX_SCHEME_CANDIDATES:
                failed_departments += 1
                break

    if failed_departments == 0:
        return candidates, "complete"
    if candidates:
        return candidates, "partial"
    return candidates, "failed"


def _discover_source(
    source: dict[str, str | None],
    checked_at: datetime,
) -> SchemeSourceResult:
    source_url = str(source["source_url"])
    is_tamil_nadu = source["source_id"] == "tamil-nadu-agriculture-schemes"
    if is_tamil_nadu:
        candidate_schemes, collection_status = (
            _collect_tamil_nadu_candidates()
        )
    else:
        candidate_schemes = []
        collection_status = "not_supported"

    def failed_source_result(
        status: Literal[
            "http_error",
            "redirected",
            "invalid_content",
            "fetch_error",
        ],
    ) -> SchemeSourceResult:
        return SchemeSourceResult(
            **source,
            status=status,
            content_status=None,
            collection_status=collection_status,
            checked_at=checked_at,
            page_title=None,
            headings=[],
            relevant_links=[],
            candidate_schemes=candidate_schemes,
        )

    try:
        with httpx.stream(
            "GET",
            source_url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=False,
            headers={"User-Agent": "AgroLens source discovery/1.0"},
        ) as response:
            response_url = str(response.url)
            response_headers = response.headers
            response_status_code = response.status_code
            response_is_error = response.is_error
            response_bytes = bytearray()
            oversized = False
            for chunk in response.iter_bytes():
                if len(response_bytes) + len(chunk) > MAX_RESPONSE_BYTES:
                    oversized = True
                    break
                response_bytes.extend(chunk)
    except httpx.RequestError:
        return failed_source_result("fetch_error")

    if 300 <= response_status_code < 400:
        return failed_source_result("redirected")

    if response_is_error:
        return failed_source_result("http_error")

    if oversized:
        return failed_source_result("invalid_content")

    if "text/html" not in response_headers.get("content-type", "").casefold():
        return failed_source_result("invalid_content")

    if urlsplit(response_url).hostname != urlsplit(source_url).hostname:
        return failed_source_result("invalid_content")

    parser = _PageMetadataParser()
    try:
        parser.feed(response_bytes.decode("utf-8", errors="replace"))
    except (ValueError, AssertionError):
        return failed_source_result("invalid_content")

    base_url = response_url
    base_host = urlsplit(base_url).hostname
    relevant_links = []
    seen_urls = set()
    for title, href in parser.links:
        if not _is_relevant(f"{title} {href}") or "{{" in title or "}}" in title:
            continue
        absolute_url = urljoin(base_url, href)
        parsed_url = urlsplit(absolute_url)
        if parsed_url.scheme != "https" or not parsed_url.hostname:
            continue
        if parsed_url.hostname != base_host:
            continue
        if absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)
        relevant_links.append(SchemeSourceLink(title=title, url=absolute_url))
        if len(relevant_links) >= MAX_LINK_COUNT:
            break

    page_text = " ".join(
        [*parser.title, *parser.headings, *(title for title, _ in parser.links)]
    ).casefold()
    if any(term in page_text for term in ERROR_PAGE_TERMS):
        content_status = "error_page_detected"
    elif any(
        _is_relevant(text)
        for text in [
            *parser.headings,
            *(title for title, _ in parser.links if "{{" not in title),
        ]
    ):
        content_status = "scheme_references_found"
    else:
        content_status = "no_scheme_references"

    return SchemeSourceResult(
        **source,
        status="available",
        content_status=content_status,
        collection_status=collection_status,
        checked_at=checked_at,
        page_title=" ".join(" ".join(parser.title).split()) or None,
        headings=parser.headings[:MAX_HEADING_COUNT],
        relevant_links=relevant_links,
        candidate_schemes=candidate_schemes,
    )


def discover_sources(force_refresh: bool = False) -> SchemeDiscoveryResponse:
    global _cache
    now = time.monotonic()
    with _cache_lock:
        if not force_refresh and _cache is not None and _cache[0] > now:
            return _cache[1].model_copy(update={"cached": True})

    checked_at = datetime.now(timezone.utc)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(
            executor.map(
                lambda source: _discover_source(source, checked_at),
                SOURCES,
            )
        )
    result = SchemeDiscoveryResponse(
        agent=AGENT_NAME,
        cached=False,
        checked_at=checked_at,
        sources=results,
    )
    with _cache_lock:
        _cache = (time.monotonic() + CACHE_TTL_SECONDS, result)
    return result


def clear_cache() -> None:
    global _cache
    with _cache_lock:
        _cache = None

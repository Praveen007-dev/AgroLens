import re
import threading
from datetime import datetime, timezone
from html.parser import HTMLParser

import httpx

from backend.app.schemas.news import NewsInput
from backend.app.schemas.news_agent import NewsCollectionResponse
from backend.app.services import news as news_service


NEWS_SOURCE_URL = (
    "https://www.pib.gov.in/newsite/pmreleases.aspx"
    "?mincode=27&reg=48&lang=2"
)
PIB_ORIGIN = "https://www.pib.gov.in"
PIB_DETAIL_PATH = "/newsite/erelcontent.aspx"
SOURCE_NAME = "Press Information Bureau — Ministry of Agriculture"
REQUEST_TIMEOUT_SECONDS = 12.0
MAX_RESPONSE_BYTES = 1_000_000
MAX_PAGE_SIZE = 20
MAX_SUMMARY_LENGTH = 5_000

_collection_lock = threading.Lock()


class NewsCollectionError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class _ReleaseListParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.releases: list[dict[str, str]] = []
        self._active = False
        self._in_date = False
        self._release: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if tag == "li" and "rel-list" in classes:
            release_id = attributes.get("id")
            if release_id and release_id.isdecimal():
                self._active = True
                self._release = {"id": release_id, "title": "", "date": ""}
        elif self._active and tag == "p" and "regDate" in classes:
            self._in_date = True

    def handle_data(self, data: str):
        if self._release is None:
            return
        key = "date" if self._in_date else "title"
        self._release[key] += data

    def handle_endtag(self, tag: str):
        if tag == "p" and self._in_date:
            self._in_date = False
        elif tag == "li" and self._active:
            if self._release is not None:
                self._release["title"] = " ".join(
                    self._release["title"].split()
                )
                self._release["date"] = " ".join(
                    self._release["date"].split()
                )
                if self._release["title"]:
                    self.releases.append(self._release)
            self._release = None
            self._active = False


class _ReleaseDetailParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._in_content = False
        self._content_depth = 0
        self._in_paragraph = False
        self._in_ministry = False
        self._ministry_depth = 0
        self._skip_depth = 0
        self._paragraph: list[str] = []
        self.paragraphs: list[str] = []
        self.ministry: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if tag in {"script", "style"}:
            self._skip_depth += 1
        if tag == "div" and attributes.get("id") == "ministry":
            self._in_ministry = True
            self._ministry_depth = 1
        elif self._in_ministry and tag == "div":
            self._ministry_depth += 1
        if tag == "div" and "contentdiv" in classes:
            self._in_content = True
            self._content_depth = 1
        elif self._in_content and tag == "div":
            self._content_depth += 1
        if self._in_content and tag == "p":
            self._in_paragraph = True
            self._paragraph = []

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        if self._in_ministry:
            self.ministry.append(data)
        if self._in_paragraph:
            self._paragraph.append(data)

    def handle_endtag(self, tag: str):
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "p" and self._in_paragraph:
            paragraph = " ".join(" ".join(self._paragraph).split())
            if paragraph:
                self.paragraphs.append(paragraph)
            self._paragraph = []
            self._in_paragraph = False
        elif tag == "div":
            if self._in_content:
                self._content_depth -= 1
            if self._in_content and self._content_depth == 0:
                self._in_content = False
            if self._in_ministry:
                self._ministry_depth -= 1
            if self._in_ministry and self._ministry_depth == 0:
                self._in_ministry = False


def _get_html(url: str) -> str:
    try:
        with httpx.stream(
            "GET",
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=False,
            headers={"User-Agent": "AgroLens PIB news reader/1.0"},
        ) as response:
            if 300 <= response.status_code < 400:
                raise NewsCollectionError(
                    502,
                    "The PIB source redirected; refusing an unverified destination.",
                )
            if response.is_error:
                raise NewsCollectionError(
                    502,
                    "The PIB source returned an HTTP error.",
                )
            if "text/html" not in response.headers.get(
                "content-type", ""
            ).casefold():
                raise NewsCollectionError(
                    502,
                    "The PIB source returned a non-HTML response.",
                )
            body = bytearray()
            for chunk in response.iter_bytes():
                if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                    raise NewsCollectionError(
                        502,
                        "The PIB page exceeded the allowed response size.",
                    )
                body.extend(chunk)
    except httpx.TimeoutException as error:
        raise NewsCollectionError(
            504,
            "The PIB source did not respond before the timeout.",
        ) from error
    except httpx.RequestError as error:
        raise NewsCollectionError(
            502,
            "Unable to connect to the PIB source.",
        ) from error
    return body.decode("utf-8", errors="replace")


def _parse_list_page(page: str) -> list[dict[str, str]]:
    parser = _ReleaseListParser()
    try:
        parser.feed(page)
    except (ValueError, AssertionError) as error:
        raise NewsCollectionError(
            502,
            "The PIB release list could not be parsed.",
        ) from error
    if not parser.releases:
        raise NewsCollectionError(
            502,
            "The PIB page did not contain any recognized releases.",
        )
    return parser.releases[:MAX_PAGE_SIZE]


def _parse_published_at(value: str) -> datetime | None:
    match = re.search(r"\((\d{2}-[A-Za-z]+(?:-| )\d{4})\)", value)
    if not match:
        return None
    for date_format in ("%d-%B-%Y", "%d-%B %Y"):
        try:
            return datetime.strptime(match.group(1), date_format).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue
    return None


def _read_release(release: dict[str, str]) -> tuple[str | None, str | None]:
    url = f"{PIB_ORIGIN}{PIB_DETAIL_PATH}?relid={release['id']}&reg=48&lang=2"
    page = _get_html(url)
    parser = _ReleaseDetailParser()
    try:
        parser.feed(page)
    except (ValueError, AssertionError):
        return None, None

    ministry = " ".join(" ".join(parser.ministry).split())
    if ministry and not any(
        term in ministry.casefold()
        for term in ("agriculture", "dare", "icar")
    ):
        return None, None

    paragraphs = [
        paragraph
        for paragraph in parser.paragraphs
        if len(paragraph) >= 40
    ]
    summary = "\n\n".join(paragraphs)
    if not summary:
        return ministry or None, None
    return ministry or None, summary[:MAX_SUMMARY_LENGTH]


def collect_news(limit: int = MAX_PAGE_SIZE) -> NewsCollectionResponse:
    if limit < 1 or limit > MAX_PAGE_SIZE:
        raise NewsCollectionError(
            422,
            f"limit must be between 1 and {MAX_PAGE_SIZE}.",
        )
    if not _collection_lock.acquire(blocking=False):
        raise NewsCollectionError(
            409,
            "A PIB news collection is already in progress.",
        )

    retrieved_at = datetime.now(timezone.utc)
    try:
        releases = _parse_list_page(_get_html(NEWS_SOURCE_URL))
        imported = 0
        duplicates = 0
        failed = 0

        for release in releases[:limit]:
            try:
                ministry, summary = _read_release(release)
                if ministry is None or summary is None:
                    failed += 1
                    continue
                article = NewsInput(
                    title=release["title"][:300],
                    summary=summary,
                    summary_type="source_provided",
                    source=SOURCE_NAME,
                    published_at=_parse_published_at(release["date"]),
                    category="Agriculture",
                    region="India",
                    original_url=(
                        f"{PIB_ORIGIN}{PIB_DETAIL_PATH}?relid={release['id']}"
                        "&reg=48&lang=2"
                    ),
                )
                try:
                    news_service.create_article(article)
                except news_service.DuplicateArticleError:
                    existing = news_service.get_article_by_url(
                        str(article.original_url)
                    )
                    if (
                        existing is not None
                        and existing.published_at is None
                        and article.published_at is not None
                    ):
                        news_service.update_article(existing.news_id, article)
                    duplicates += 1
                else:
                    imported += 1
            except NewsCollectionError:
                failed += 1

        return NewsCollectionResponse(
            source=NEWS_SOURCE_URL,
            retrieved_at=retrieved_at,
            listed=min(len(releases), limit),
            imported=imported,
            duplicates=duplicates,
            failed=failed,
        )
    finally:
        _collection_lock.release()

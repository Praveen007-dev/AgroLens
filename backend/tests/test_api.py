import csv
import io
import sqlite3
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app import database
from backend.app.config import get_setting
from backend.app.main import app
from backend.app.services import mandi as mandi_service
from backend.app.services import news_agent as news_agent_service
from backend.app.services import scheme_agent as scheme_agent_service
from backend.app.services import weather as weather_service


class FakeStreamResponse:
    def __init__(
        self,
        url,
        body=b"<html><title>Official schemes</title></html>",
        status_code=200,
        content_type="text/html; charset=utf-8",
    ):
        self.url = httpx.URL(url)
        self.headers = {"content-type": content_type}
        self.status_code = status_code
        self.is_error = status_code >= 400
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def iter_bytes(self):
        yield self.body


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test_agrolens.db")
    monkeypatch.setenv("AGROLENS_SCHEMES_ADMIN_TOKEN", "test-admin-token")
    monkeypatch.setenv("AGROLENS_NEWS_ADMIN_TOKEN", "test-news-token")
    monkeypatch.setenv("AGROLENS_MANDI_ADMIN_TOKEN", "test-mandi-token")
    weather_service.clear_cache()
    scheme_agent_service.clear_cache()
    with TestClient(app) as test_client:
        yield test_client
    weather_service.clear_cache()
    scheme_agent_service.clear_cache()


def create_sample_scan(**overrides):
    payload = {
        "scan_id": str(uuid4()),
        "crop": "TestTomato",
        "scan_timestamp": "2026-11-04T09:30:00Z",
        "model_version": "TestModel-v1",
        "disease_label": "Early Blight",
        "confidence": 0.94,
        "image_ref": "test-image-001",
        "location_consent": False,
    }
    payload.update(overrides)
    return payload


def submit_scan(client, **overrides):
    payload = create_sample_scan(**overrides)
    response = client.post("/api/scans", json=payload)
    assert response.status_code == 201, response.text
    return payload, response


def create_sample_scheme(**overrides):
    payload = {
        "scheme_name": "Test Agriculture Support Scheme",
        "government_level": "state",
        "state": "Karnataka",
        "description": None,
        "eligibility": None,
        "benefits": None,
        "required_documents": None,
        "application_deadline": None,
        "official_url": None,
        "source_name": "Test official source",
        "source_url": "https://example.gov.in/schemes/test",
        "last_verified_at": "2026-11-04T10:00:00Z",
    }
    payload.update(overrides)
    return payload


def create_scheme(client, **overrides):
    response = client.post(
        "/api/schemes",
        json=create_sample_scheme(**overrides),
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_weather_provider_payload(days=1):
    forecast_days = []
    for day in range(days):
        forecast_days.append(
            {
                "date": f"2026-11-{4 + day:02}",
                "day": {
                    "mintemp_c": 18.0 + day,
                    "maxtemp_c": 28.0 + day,
                    "avgtemp_c": 23.0 + day,
                    "maxwind_kph": 15.0,
                    "totalprecip_mm": 1.2,
                    "daily_chance_of_rain": 40,
                    "daily_chance_of_snow": 0,
                    "condition": {
                        "text": "Partly cloudy",
                        "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png",
                        "code": 1003,
                    },
                },
            }
        )
    return {
        "location": {
            "name": "Bengaluru",
            "region": "Karnataka",
            "country": "India",
            "lat": 12.97,
            "lon": 77.59,
            "localtime": "2026-11-04 15:00",
        },
        "current": {
            "last_updated": "2026-11-04 14:45",
            "temp_c": 25.0,
            "feelslike_c": 26.0,
            "humidity": 65,
            "wind_kph": 12.0,
            "precip_mm": 0.0,
            "is_day": 1,
            "condition": {
                "text": "Sunny",
                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                "code": 1000,
            },
        },
        "forecast": {"forecastday": forecast_days},
        "alerts": {
            "alert": [
                {
                    "headline": "Weather advisory",
                    "severity": "Moderate",
                    "event": "Heavy rain",
                    "effective": "2026-11-04T16:00:00+00:00",
                    "expires": "2026-11-04T22:00:00+00:00",
                    "desc": "Provider-issued alert description",
                    "instruction": "Provider-issued instructions",
                }
            ]
        },
    }


def create_open_meteo_payload(days=1):
    return {
        "current": {
            "time": "2026-11-05T13:00",
            "temperature_2m": 25.0,
            "relative_humidity_2m": 65,
            "apparent_temperature": 26.0,
            "is_day": 1,
            "precipitation": 0.0,
            "weather_code": 0,
            "wind_speed_10m": 12.0,
        },
        "daily": {
            "time": [f"2026-11-{5 + index:02}" for index in range(days)],
            "weather_code": [2] * days,
            "temperature_2m_max": [28.0] * days,
            "temperature_2m_min": [18.0] * days,
            "temperature_2m_mean": [23.0] * days,
            "precipitation_probability_max": [40] * days,
            "precipitation_sum": [1.2] * days,
            "wind_speed_10m_max": [15.0] * days,
        },
    }


def create_sample_news(**overrides):
    payload = {
        "title": "Synthetic agriculture news test article",
        "summary": None,
        "summary_type": None,
        "source": "Test Agriculture Department",
        "published_at": "2026-11-04T10:00:00Z",
        "category": "farming",
        "region": "Karnataka",
        "original_url": "https://example.gov.in/news/agriculture-001",
    }
    payload.update(overrides)
    return payload


def create_mandi_provider_record(**overrides):
    record = {
        "State": "Karnataka",
        "District": "Bengaluru Urban",
        "Market": "Bengaluru",
        "Commodity": "Tomato",
        "Variety": "Local",
        "Grade": "FAQ",
        "Arrival_Date": "04/11/2026",
        "Min_Price": "1800",
        "Max_Price": "2400",
        "Modal_Price": "2100",
    }
    record.update(overrides)
    return record


def mock_mandi_provider(monkeypatch, records):
    calls = []

    def fake_get(url, *, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return SimpleNamespace(
            is_error=False,
            json=lambda: {"records": records},
        )

    monkeypatch.setattr(mandi_service.httpx, "get", fake_get)
    return calls


def create_news(client, **overrides):
    response = client.post(
        "/api/news",
        json=create_sample_news(**overrides),
        headers={"X-News-Admin-Token": "test-news-token"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def mock_weatherapi_response(monkeypatch, days=1):
    calls = []

    def fake_get(url, *, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return SimpleNamespace(
            is_error=False,
            json=lambda: create_weather_provider_payload(days),
        )

    monkeypatch.setattr(weather_service.httpx, "get", fake_get)
    return calls


def mock_open_meteo_response(monkeypatch, days=1):
    calls = []

    def fake_get(url, *, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        if url == weather_service.OPEN_METEO_GEOCODING_URL:
            return SimpleNamespace(
                is_error=False,
                json=lambda: {
                    "results": [
                        {
                            "name": "Bengaluru",
                            "admin1": "Karnataka",
                            "country": "India",
                            "latitude": 12.97,
                            "longitude": 77.59,
                        }
                    ]
                },
            )
        return SimpleNamespace(
            is_error=False,
            json=lambda: create_open_meteo_payload(days),
        )

    monkeypatch.setattr(weather_service.httpx, "get", fake_get)
    return calls


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_secret_settings_read_environment_without_exposing_values(
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", "unit-test-secret")
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "   ")

    assert get_setting("AGROLENS_WEATHERAPI_KEY") == "unit-test-secret"
    assert get_setting("AGROLENS_DATA_GOV_IN_API_KEY") is None


def test_submit_scan_returns_scan_id_and_success(client):
    payload = create_sample_scan()

    response = client.post("/api/scans", json=payload)

    assert response.status_code == 201, response.text
    assert response.json()["scan_id"] == payload["scan_id"]
    assert response.json()["submission_status"] == "success"


def test_submit_scan_generates_id_when_omitted(client):
    payload = create_sample_scan()
    payload.pop("scan_id")

    response = client.post("/api/scans", json=payload)

    assert response.status_code == 201, response.text
    assert response.json()["scan_id"]
    assert response.json()["scan_id"] != "None"


def test_submit_scan_rejects_duplicate_id_without_overwriting(client):
    payload = create_sample_scan()
    first_response = client.post("/api/scans", json=payload)
    assert first_response.status_code == 201, first_response.text

    duplicate_response = client.post(
        "/api/scans",
        json={**payload, "crop": "DifferentCrop"},
    )

    assert duplicate_response.status_code == 409
    retrieved = client.get(f"/api/scans/{payload['scan_id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["crop"] == payload["crop"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("crop", ""),
        ("confidence", -0.01),
        ("confidence", 1.01),
        ("scan_timestamp", "not-a-timestamp"),
    ],
)
def test_submit_scan_rejects_invalid_values(client, field, value):
    response = client.post(
        "/api/scans",
        json=create_sample_scan(**{field: value}),
    )

    assert response.status_code == 422


def test_submit_scan_rejects_unknown_fields(client):
    response = client.post(
        "/api/scans",
        json=create_sample_scan(unexpected_field="not allowed"),
    )

    assert response.status_code == 422


def test_retrieve_scan_returns_all_scan_and_prediction_fields(client):
    payload, _ = submit_scan(client)

    response = client.get(f"/api/scans/{payload['scan_id']}")

    assert response.status_code == 200
    record = response.json()
    assert record["scan_id"] == payload["scan_id"]
    assert record["crop"] == payload["crop"]
    assert record["disease_label"] == payload["disease_label"]
    assert record["confidence"] == payload["confidence"]
    assert record["image_ref"] == payload["image_ref"]
    assert record["verification_status"] == "pending"


def test_retrieve_missing_scan_returns_404(client):
    response = client.get(f"/api/scans/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Scan record not found."


def test_list_scans_filters_by_crop_and_disease(client):
    submit_scan(
        client,
        scan_timestamp="2026-11-04T09:30:00Z",
        crop="Tomato",
        disease_label="Early Blight",
    )
    submit_scan(
        client,
        scan_timestamp="2026-11-04T10:30:00Z",
        crop="Potato",
        disease_label="Late Blight",
    )
    submit_scan(
        client,
        scan_timestamp="2026-11-04T11:30:00Z",
        crop="Tomato",
        disease_label="Leaf Mold",
    )

    response = client.get(
        "/api/scans",
        params={"crop": "Tomato", "disease": "Early Blight"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["count"] == 1
    assert body["scans"][0]["crop"] == "Tomato"
    assert body["scans"][0]["disease_label"] == "Early Blight"


def test_list_scans_paginates_in_descending_timestamp_order(client):
    ids = []
    for hour in (9, 10, 11):
        payload, _ = submit_scan(
            client,
            scan_timestamp=f"2026-11-04T{hour:02}:00:00Z",
        )
        ids.append(payload["scan_id"])

    first_page = client.get("/api/scans", params={"page": 1, "limit": 2})
    second_page = client.get("/api/scans", params={"page": 2, "limit": 2})

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert [row["scan_id"] for row in first_page.json()["scans"]] == [
        ids[2],
        ids[1],
    ]
    assert [row["scan_id"] for row in second_page.json()["scans"]] == [ids[0]]
    assert first_page.json()["total"] == 3
    assert first_page.json()["total_pages"] == 2
    assert first_page.json()["has_next"] is True
    assert second_page.json()["has_previous"] is True


@pytest.mark.parametrize(
    "params",
    [{"page": 0}, {"limit": 0}, {"limit": 101}],
)
def test_list_scans_rejects_invalid_pagination(client, params):
    response = client.get("/api/scans", params=params)

    assert response.status_code == 422


def test_dashboard_summary_counts_only_current_database_records(client):
    submit_scan(client, crop="Tomato", disease_label="Early Blight")
    submit_scan(client, crop="Tomato", disease_label="Early Blight")
    submit_scan(client, crop="Potato", disease_label="Late Blight")

    response = client.get("/api/analytics/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_scans": 3,
        "crop_counts": {"Tomato": 2, "Potato": 1},
        "disease_counts": {"Early Blight": 2, "Late Blight": 1},
        "verification_counts": {"pending": 3},
    }


def test_submit_scan_persists_feedback_and_consenting_metadata(client):
    payload, _ = submit_scan(
        client,
        farmer_confirmed_label="Early Blight",
        feedback_text="Synthetic test feedback",
        location_consent=True,
        latitude=12.97,
        longitude=77.59,
        environmental_data={"temperature_c": 24.5},
        additional_metadata={"source": "test"},
    )

    connection = database.get_connection()
    try:
        feedback = connection.execute(
            "SELECT farmer_confirmed_label, feedback_text "
            "FROM farmer_feedback WHERE scan_id = ?",
            (payload["scan_id"],),
        ).fetchone()
        metadata = connection.execute(
            "SELECT location_consent, latitude, longitude, "
            "environmental_data, additional_metadata "
            "FROM optional_metadata WHERE scan_id = ?",
            (payload["scan_id"],),
        ).fetchone()
    finally:
        connection.close()

    assert tuple(feedback) == ("Early Blight", "Synthetic test feedback")
    assert metadata["location_consent"] == 1
    assert metadata["latitude"] == 12.97
    assert metadata["longitude"] == 77.59
    assert metadata["environmental_data"] == '{"temperature_c": 24.5}'
    assert metadata["additional_metadata"] == '{"source": "test"}'


def test_location_is_not_stored_without_consent(client):
    payload, _ = submit_scan(
        client,
        location_consent=False,
        latitude=12.97,
        longitude=77.59,
        environmental_data={"temperature_c": 24.5},
    )

    connection = database.get_connection()
    try:
        metadata = connection.execute(
            "SELECT location_consent, latitude, longitude "
            "FROM optional_metadata WHERE scan_id = ?",
            (payload["scan_id"],),
        ).fetchone()
    finally:
        connection.close()

    assert metadata["location_consent"] == 0
    assert metadata["latitude"] is None
    assert metadata["longitude"] is None


def test_json_export_contains_research_fields_and_excludes_private_data(client):
    payload, _ = submit_scan(
        client,
        farmer_confirmed_label="Early Blight",
        feedback_text="Private feedback",
        environmental_data={"temperature_c": 24.5},
    )

    response = client.get("/api/export/scans?format=json")

    assert response.status_code == 200
    records = response.json()
    assert len(records) == 1
    assert records[0]["scan_id"] == payload["scan_id"]
    assert records[0]["disease_label"] == payload["disease_label"]
    assert "feedback_text" not in records[0]
    assert "latitude" not in records[0]
    assert "environmental_data" not in records[0]


def test_csv_export_contains_header_and_scan(client):
    payload, _ = submit_scan(client)

    response = client.get("/api/export/scans?format=csv")

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == 1
    assert rows[0]["scan_id"] == payload["scan_id"]
    assert rows[0]["disease_label"] == payload["disease_label"]


def test_export_rejects_unsupported_format(client):
    response = client.get("/api/export/scans?format=xml")

    assert response.status_code == 422


def test_schemes_list_is_empty_until_verified_records_are_added(client):
    response = client.get("/api/schemes")

    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "total": 0,
        "limit": 20,
        "offset": 0,
        "schemes": [],
    }


def test_create_and_retrieve_scheme(client):
    created = create_scheme(client)

    response = client.get(f"/api/schemes/{created['scheme_id']}")

    assert response.status_code == 200
    record = response.json()
    assert record["scheme_name"] == "Test Agriculture Support Scheme"
    assert record["government_level"] == "state"
    assert record["state"] == "Karnataka"
    assert record["benefits"] is None
    assert record["application_deadline"] is None
    assert record["source_name"] == "Test official source"
    assert record["last_verified_at"] == "2026-11-04T10:00:00Z"


def test_scheme_creation_requires_admin_token(client):
    response = client.post(
        "/api/schemes",
        json=create_sample_scheme(),
    )

    assert response.status_code == 401


def test_scheme_creation_requires_configured_admin_token(client, monkeypatch):
    monkeypatch.delenv("AGROLENS_SCHEMES_ADMIN_TOKEN")

    response = client.post(
        "/api/schemes",
        json=create_sample_scheme(),
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )

    assert response.status_code == 503


def test_schemes_can_be_filtered_and_paginated(client):
    create_scheme(client, state="Karnataka")
    create_scheme(
        client,
        scheme_name="Tamil Nadu Test Scheme",
        state="Tamil Nadu",
    )
    create_scheme(
        client,
        scheme_name="Central Test Scheme",
        government_level="central",
        state=None,
    )

    response = client.get(
        "/api/schemes",
        params={
            "government_level": "state",
            "state": "Tamil Nadu",
            "limit": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["count"] == 1
    assert response.json()["schemes"][0]["state"] == "Tamil Nadu"


@pytest.mark.parametrize(
    "overrides",
    [
        {"government_level": "state", "state": None},
        {"government_level": "other"},
        {"source_url": "not-a-url"},
        {"last_verified_at": "not-a-timestamp"},
    ],
)
def test_scheme_creation_rejects_invalid_records(client, overrides):
    response = client.post(
        "/api/schemes",
        json=create_sample_scheme(**overrides),
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )

    assert response.status_code == 422


def test_update_scheme_requires_admin_and_updates_verification_data(client):
    created = create_scheme(client)
    updated_payload = create_sample_scheme(
        scheme_name="Updated Test Agriculture Scheme",
        benefits="Unknown",
        last_verified_at="2026-11-05T10:00:00Z",
    )

    response = client.put(
        f"/api/schemes/{created['scheme_id']}",
        json=updated_payload,
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )

    assert response.status_code == 200
    assert response.json()["scheme_name"] == "Updated Test Agriculture Scheme"
    assert response.json()["benefits"] == "Unknown"
    assert response.json()["last_verified_at"] == "2026-11-05T10:00:00Z"


def test_scheme_update_and_detail_return_404_for_unknown_id(client):
    unknown_id = str(uuid4())

    detail = client.get(f"/api/schemes/{unknown_id}")
    update = client.put(
        f"/api/schemes/{unknown_id}",
        json=create_sample_scheme(),
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )

    assert detail.status_code == 404
    assert update.status_code == 404


def test_schemes_reject_invalid_filters_and_pagination(client):
    invalid_level = client.get(
        "/api/schemes",
        params={"government_level": "federal"},
    )
    invalid_limit = client.get("/api/schemes", params={"limit": 101})
    invalid_offset = client.get("/api/schemes", params={"offset": -1})

    assert invalid_level.status_code == 422
    assert invalid_limit.status_code == 422
    assert invalid_offset.status_code == 422


def test_scheme_agent_requires_admin_token(client, monkeypatch):
    def unexpected_request(*args, **kwargs):
        raise AssertionError("Source requests must not run without admin auth.")

    monkeypatch.setattr(scheme_agent_service.httpx, "stream", unexpected_request)

    response = client.post("/api/schemes/agent/discover")

    assert response.status_code == 401


def test_scheme_agent_read_is_available_without_admin_token(client, monkeypatch):
    def fake_stream(method, url, **kwargs):
        return FakeStreamResponse(
            url,
            body=(
                b"<html><title>Official schemes</title>"
                b"<h1>Government schemes</h1></html>"
            ),
        )

    monkeypatch.setattr(scheme_agent_service.httpx, "stream", fake_stream)
    monkeypatch.setattr(
        scheme_agent_service.httpx,
        "post",
        lambda url, **kwargs: SimpleNamespace(
            status_code=200,
            is_error=False,
            content=b"[]",
            json=lambda: [],
        ),
    )

    response = client.get("/api/schemes/agent/discover")

    assert response.status_code == 200
    assert len(response.json()["sources"]) == len(scheme_agent_service.SOURCES)


def test_scheme_agent_checks_allowlisted_sources_without_importing_schemes(
    client,
    monkeypatch,
):
    html = (
        b"<html><head><title>Official Agriculture</title></head><body>"
        b"<h1>Farmer support schemes</h1>"
        b'<a href="/schemes/details">Scheme Details</a>'
        b'<a href="/schemes/translated">{{lang==en?Schemes:}}</a>'
        b'<a href="/farmers">Farmer Registration</a>'
        b'<a href="https://external.example/scheme">External Scheme</a>'
        b"</body></html>"
    )
    requests = []

    def fake_stream(method, url, **kwargs):
        requests.append((method, url, kwargs))
        return FakeStreamResponse(url, body=html)

    api_calls = []

    def fake_post(url, **kwargs):
        department = url.rsplit("/", maxsplit=1)[-1]
        api_calls.append((url, kwargs))
        return SimpleNamespace(
            status_code=200,
            is_error=False,
            content=b"[]",
            json=lambda: [
                {
                    "scheme_id": department,
                    "Scheme_Name": f"Live scheme {department}",
                    "Scheme_Name_Tamil": None,
                }
            ],
        )

    monkeypatch.setattr(scheme_agent_service.httpx, "stream", fake_stream)
    monkeypatch.setattr(scheme_agent_service.httpx, "post", fake_post)

    response = client.post(
        "/api/schemes/agent/discover?refresh=true",
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["agent"] == scheme_agent_service.AGENT_NAME
    assert result["cached"] is False
    assert len(result["sources"]) == len(scheme_agent_service.SOURCES) == 6
    assert len(requests) == 6
    assert all(request[0] == "GET" for request in requests)
    assert all(
        request[2]["timeout"] == scheme_agent_service.REQUEST_TIMEOUT_SECONDS
        for request in requests
    )
    assert all(request[2]["follow_redirects"] is False for request in requests)
    assert all(source["status"] == "available" for source in result["sources"])
    assert all(
        source["page_title"] == "Official Agriculture"
        for source in result["sources"]
    )
    assert all(
        source["content_status"] == "scheme_references_found"
        and source["relevant_links"][0]["title"] == "Scheme Details"
        and len(source["relevant_links"]) == 1
        for source in result["sources"]
    )
    tamil_nadu = next(
        source
        for source in result["sources"]
        if source["source_id"] == "tamil-nadu-agriculture-schemes"
    )
    assert tamil_nadu["collection_status"] == "complete"
    assert [item["name"] for item in tamil_nadu["candidate_schemes"]] == [
        "Live scheme A",
        "Live scheme H",
        "Live scheme E",
        "Live scheme M",
    ]
    assert all(
        item["review_status"] == "unverified"
        for item in tamil_nadu["candidate_schemes"]
    )
    assert len(api_calls) == len(scheme_agent_service.TAMIL_NADU_DEPARTMENTS)
    assert client.get("/api/schemes").json()["total"] == 0


def test_scheme_agent_reports_source_failures_and_ignores_non_html(
    client,
    monkeypatch,
):
    sources = scheme_agent_service.SOURCES

    def fake_stream(method, url, **kwargs):
        index = next(
            i for i, source in enumerate(sources) if source["source_url"] == url
        )
        if index == 0:
            return FakeStreamResponse(url, status_code=403)
        if index == 1:
            raise httpx.TimeoutException(
                "simulated timeout",
                request=httpx.Request("GET", url),
            )
        if index == 2:
            return FakeStreamResponse(url, content_type="application/json")
        if index == 3:
            return FakeStreamResponse(url, status_code=302)
        if index == 4:
            return FakeStreamResponse(
                url,
                body=b"x" * (scheme_agent_service.MAX_RESPONSE_BYTES + 1),
            )
        if index == 5:
            return FakeStreamResponse(
                url,
                body=(
                    b"<html><title>Official site</title>"
                    b"<h1>Something went wrong. Please try again later.</h1>"
                    b"</html>"
                ),
            )
        return FakeStreamResponse(url)

    monkeypatch.setattr(scheme_agent_service.httpx, "stream", fake_stream)
    monkeypatch.setattr(
        scheme_agent_service.httpx,
        "post",
        lambda url, **kwargs: SimpleNamespace(
            status_code=200,
            is_error=False,
            content=b"[]",
            json=lambda: [],
        ),
    )

    response = client.post(
        "/api/schemes/agent/discover?refresh=true",
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )

    assert response.status_code == 200
    statuses = [source["status"] for source in response.json()["sources"]]
    assert statuses == [
        "http_error",
        "fetch_error",
        "invalid_content",
        "redirected",
        "invalid_content",
        "available",
    ]
    assert response.json()["sources"][-1]["content_status"] == "error_page_detected"


def test_scheme_agent_collects_tamil_nadu_candidates_when_page_times_out(
    client,
    monkeypatch,
):
    source_url = next(
        source["source_url"]
        for source in scheme_agent_service.SOURCES
        if source["source_id"] == "tamil-nadu-agriculture-schemes"
    )
    department_calls = []

    def fake_stream(method, url, **kwargs):
        if url == source_url:
            raise httpx.TimeoutException(
                "simulated Tamil Nadu page timeout",
                request=httpx.Request("GET", url),
            )
        return FakeStreamResponse(url)

    def fake_post(url, **kwargs):
        department = url.rsplit("/", maxsplit=1)[-1]
        department_calls.append(department)
        records = (
            [
                {
                    "scheme_id": "tn-ag-001",
                    "Scheme_Name": "Tamil Nadu Farmer Support",
                    "Scheme_Name_Tamil": "உழவர் உதவி",
                }
            ]
            if department == "A"
            else []
        )
        return SimpleNamespace(
            status_code=200,
            is_error=False,
            content=b"[]",
            json=lambda: records,
        )

    monkeypatch.setattr(scheme_agent_service.httpx, "stream", fake_stream)
    monkeypatch.setattr(scheme_agent_service.httpx, "post", fake_post)

    response = client.post(
        "/api/schemes/agent/discover?refresh=true",
        headers={"X-Schemes-Admin-Token": "test-admin-token"},
    )

    assert response.status_code == 200
    tamil_nadu = next(
        source
        for source in response.json()["sources"]
        if source["source_id"] == "tamil-nadu-agriculture-schemes"
    )
    assert tamil_nadu["status"] == "fetch_error"
    assert tamil_nadu["collection_status"] == "complete"
    assert tamil_nadu["candidate_schemes"] == [
        {
            "source_record_id": "tn-ag-001",
            "department": "Agriculture",
            "name": "Tamil Nadu Farmer Support",
            "local_name": "உழவர் உதவி",
            "review_status": "unverified",
        }
    ]
    assert department_calls == [
        code for code, _ in scheme_agent_service.TAMIL_NADU_DEPARTMENTS
    ]
    assert client.get("/api/schemes").json()["total"] == 0


def test_scheme_agent_caches_and_can_be_refreshed(client, monkeypatch):
    calls = []

    def fake_stream(method, url, **kwargs):
        calls.append(url)
        return FakeStreamResponse(url)

    monkeypatch.setattr(
        scheme_agent_service.httpx,
        "post",
        lambda url, **kwargs: SimpleNamespace(
            status_code=200,
            is_error=False,
            content=b"[]",
            json=lambda: [],
        ),
    )
    monkeypatch.setattr(scheme_agent_service.httpx, "stream", fake_stream)
    headers = {"X-Schemes-Admin-Token": "test-admin-token"}

    first = client.post("/api/schemes/agent/discover", headers=headers)
    cached = client.post("/api/schemes/agent/discover", headers=headers)
    refreshed = client.post(
        "/api/schemes/agent/discover?refresh=true",
        headers=headers,
    )

    assert first.status_code == cached.status_code == refreshed.status_code == 200
    assert first.json()["cached"] is False
    assert cached.json()["cached"] is True
    assert refreshed.json()["cached"] is False
    assert len(calls) == 2 * len(scheme_agent_service.SOURCES)


def test_scheme_table_initialization_preserves_existing_scan_records(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "existing_agrolens.db"
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("""
            CREATE TABLE scan_records (
                scan_id TEXT PRIMARY KEY,
                crop TEXT NOT NULL,
                scan_timestamp TEXT NOT NULL,
                model_version TEXT NOT NULL,
                image_ref TEXT,
                verification_status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute(
            """
            INSERT INTO scan_records (
                scan_id, crop, scan_timestamp, model_version
            ) VALUES (?, ?, ?, ?)
            """,
            ("existing-scan", "Tomato", "2026-11-04T09:30:00Z", "v1"),
        )
        connection.commit()
    finally:
        connection.close()

    monkeypatch.setattr(database, "DB_PATH", database_path)
    database.init_db()

    connection = database.get_connection()
    try:
        existing_scan = connection.execute(
            "SELECT crop FROM scan_records WHERE scan_id = ?",
            ("existing-scan",),
        ).fetchone()
        schemes_table = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'agriculture_schemes'
            """
        ).fetchone()
    finally:
        connection.close()

    assert existing_scan["crop"] == "Tomato"
    assert schemes_table is not None


def test_current_weather_endpoint_returns_normalized_provider_data(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", "test-weather-key")
    calls = mock_weatherapi_response(monkeypatch)

    response = client.get(
        "/api/weather/current",
        params={"location": "12.97,77.59"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "WeatherAPI.com"
    assert body["location"]["name"] == "Bengaluru"
    assert body["current"]["temperature_c"] == 25.0
    assert body["current"]["condition"]["text"] == "Sunny"
    assert calls[0]["params"]["q"] == "12.97,77.59"
    assert calls[0]["params"]["key"] == "test-weather-key"
    assert calls[0]["params"]["days"] == 1
    assert calls[0]["params"]["aqi"] == "no"
    assert calls[0]["params"]["alerts"] == "yes"


def test_forecast_endpoint_returns_requested_days_and_provider_alerts(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", "test-weather-key")
    calls = mock_weatherapi_response(monkeypatch, days=3)

    response = client.get(
        "/api/weather/forecast",
        params={"location": "Bengaluru, India", "days": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["forecast"]) == 3
    assert body["forecast"][0]["chance_of_rain_percent"] == 40
    assert body["alerts"][0]["event"] == "Heavy rain"
    assert body["alerts"][0]["instruction"] == "Provider-issued instructions"
    assert calls[0]["params"]["days"] == 3


def test_weather_uses_open_meteo_when_weatherapi_is_not_configured(
    client,
    monkeypatch,
):
    monkeypatch.delenv("AGROLENS_WEATHERAPI_KEY", raising=False)
    calls = mock_open_meteo_response(monkeypatch)

    response = client.get(
        "/api/weather/current",
        params={"location": "Bengaluru"},
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "Open-Meteo"
    assert response.json()["location"]["name"] == "Bengaluru"
    assert response.json()["current"]["condition"]["text"] == "Clear sky"
    assert len(calls) == 2


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/api/weather/current", {"location": ""}),
        ("/api/weather/forecast", {"location": "Bengaluru", "days": 0}),
        ("/api/weather/forecast", {"location": "Bengaluru", "days": 15}),
    ],
)
def test_weather_endpoints_validate_location_and_forecast_range(
    client,
    path,
    params,
):
    response = client.get(path, params=params)

    assert response.status_code == 422


def test_weather_forecast_uses_cache_for_repeated_requests(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", "test-weather-key")
    calls = mock_weatherapi_response(monkeypatch, days=2)
    params = {"location": "Bengaluru", "days": 2}

    first = client.get("/api/weather/forecast", params=params)
    second = client.get("/api/weather/forecast", params=params)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert len(calls) == 1


def test_weather_location_not_found_maps_to_404(client, monkeypatch):
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", "test-weather-key")

    def fake_get(url, *, params, timeout):
        return SimpleNamespace(
            is_error=True,
            status_code=400,
            json=lambda: {"error": {"code": 1006}},
        )

    monkeypatch.setattr(weather_service.httpx, "get", fake_get)

    response = client.get(
        "/api/weather/current",
        params={"location": "UnknownPlace"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Weather location was not found."


def test_weather_provider_auth_failure_falls_back_to_open_meteo(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", "test-weather-key")
    primary_calls = []
    fallback_calls = []

    def reject_primary(location, days, api_key):
        primary_calls.append((location, days, api_key))
        raise weather_service.WeatherServiceError(
            503,
            "Weather provider credentials were rejected.",
        )

    monkeypatch.setattr(
        weather_service,
        "_fetch_from_provider",
        reject_primary,
    )
    fallback_response = weather_service._normalize_response(
        create_weather_provider_payload()
    ).model_copy(update={"provider": weather_service.OPEN_METEO_PROVIDER_NAME})

    def open_meteo_fallback(location, days):
        fallback_calls.append((location, days))
        return fallback_response

    monkeypatch.setattr(
        weather_service,
        "_fetch_from_open_meteo",
        open_meteo_fallback,
    )

    response = client.get(
        "/api/weather/current",
        params={"location": "Bengaluru"},
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "Open-Meteo"
    assert primary_calls == [("Bengaluru", 1, "test-weather-key")]
    assert fallback_calls == [("Bengaluru", 1)]


def test_weather_provider_timeout_returns_504_without_leaking_credentials(
    client,
    monkeypatch,
):
    secret = "test-weather-key"
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", secret)

    def fake_get(url, *, params, timeout):
        raise httpx.TimeoutException("provider timeout")

    monkeypatch.setattr(weather_service.httpx, "get", fake_get)

    response = client.get(
        "/api/weather/current",
        params={"location": "Bengaluru"},
    )

    assert response.status_code == 504
    assert secret not in response.text


def test_weather_provider_invalid_response_returns_502(client, monkeypatch):
    monkeypatch.setenv("AGROLENS_WEATHERAPI_KEY", "test-weather-key")

    def fake_get(url, *, params, timeout):
        return SimpleNamespace(is_error=False, json=lambda: {})

    monkeypatch.setattr(weather_service.httpx, "get", fake_get)

    def fail_open_meteo(location, days):
        raise weather_service.WeatherServiceError(
            502,
            "The public weather provider returned an invalid response.",
        )

    monkeypatch.setattr(
        weather_service,
        "_fetch_from_open_meteo",
        fail_open_meteo,
    )

    response = client.get(
        "/api/weather/current",
        params={"location": "Bengaluru"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "The public weather provider returned an invalid response."
    )


def test_news_list_is_empty_until_articles_are_imported(client):
    response = client.get("/api/news")

    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "total": 0,
        "limit": 20,
        "offset": 0,
        "articles": [],
    }


def test_pib_news_collection_requires_admin_token(client, monkeypatch):
    def unexpected_request(*args, **kwargs):
        raise AssertionError("PIB requests must not run without admin auth.")

    monkeypatch.setattr(news_agent_service.httpx, "stream", unexpected_request)

    response = client.post("/api/news/agent/collect")

    assert response.status_code == 401


def test_pib_news_agent_collects_source_articles_and_deduplicates(
    client,
    monkeypatch,
):
    releases = [
        {
            "id": "12345",
            "title": "Agricultural research partnership announced",
            "date": "(04-November 2026)",
        },
        {
            "id": "12346",
            "title": "New crop support programme launched",
            "date": "(03-November-2026)",
        },
    ]
    listing = "".join(
        f'<li class="rel rel-list" id="{release["id"]}">'
        f'{release["title"]}<p class="regDate">{release["date"]}</p></li>'
        for release in releases
    )
    list_html = (
        "<html><body>"
        f'<ul class="rel-display11">{listing}</ul>'
        "</body></html>"
    )
    detail_html = (
        "<html><body>"
        '<div class="mddiv content-ministry" id="ministry">'
        "Ministry of Agriculture &amp; Farmers Welfare"
        "<span>04-November, 2026 10:00 IST</span></div>"
        '<div class="contentdiv"><div class="headline">'
        "<h1>Official release heading</h1></div>"
        "<p>This is the official PIB article text containing source details "
        "about agricultural research, farmers, and the announced programme."
        "</p><p>The release provides additional verified facts from the "
        "Ministry of Agriculture and Farmers Welfare.</p></div>"
        "</body></html>"
    )
    calls = []

    def fake_stream(method, url, **kwargs):
        calls.append(url)
        if url == news_agent_service.NEWS_SOURCE_URL:
            return FakeStreamResponse(url, body=list_html.encode())
        assert url.startswith(news_agent_service.PIB_ORIGIN)
        assert news_agent_service.PIB_DETAIL_PATH in url
        return FakeStreamResponse(url, body=detail_html.encode())

    monkeypatch.setattr(news_agent_service.httpx, "stream", fake_stream)
    headers = {"X-News-Admin-Token": "test-news-token"}

    first = client.post(
        "/api/news/agent/collect?limit=2",
        headers=headers,
    )
    second = client.post(
        "/api/news/agent/collect?limit=2",
        headers=headers,
    )

    assert first.status_code == 200
    assert first.json()["listed"] == 2
    assert first.json()["imported"] == 2
    assert first.json()["duplicates"] == 0
    assert first.json()["failed"] == 0
    assert second.status_code == 200
    assert second.json()["imported"] == 0
    assert second.json()["duplicates"] == 2
    assert len(calls) == 6

    articles = client.get("/api/news", params={"category": "Agriculture"})
    assert articles.status_code == 200
    assert articles.json()["total"] == 2
    record = articles.json()["articles"][0]
    assert record["source"] == news_agent_service.SOURCE_NAME
    assert record["summary_type"] == "source_provided"
    assert record["published_at"] == "2026-11-04T00:00:00Z"
    assert "official PIB article text" in record["summary"]
    assert "relid=1234" in record["original_url"]
    assert record["region"] == "India"


def test_pib_news_collection_reports_upstream_failure(client, monkeypatch):
    monkeypatch.setattr(
        news_agent_service.httpx,
        "stream",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            httpx.TimeoutException("simulated PIB timeout")
        ),
    )

    response = client.post(
        "/api/news/agent/collect",
        headers={"X-News-Admin-Token": "test-news-token"},
    )

    assert response.status_code == 504
    assert response.json()["detail"] == (
        "The PIB source did not respond before the timeout."
    )


def test_import_and_retrieve_news_preserves_original_source_and_url(client):
    created = create_news(
        client,
        summary="Summary from the original government article.",
        summary_type="source_provided",
    )

    response = client.get(f"/api/news/{created['news_id']}")

    assert response.status_code == 200
    record = response.json()
    assert record["title"] == "Synthetic agriculture news test article"
    assert record["summary"] == (
        "Summary from the original government article."
    )
    assert record["summary_type"] == "source_provided"
    assert record["source"] == "Test Agriculture Department"
    assert record["original_url"] == (
        "https://example.gov.in/news/agriculture-001"
    )


def test_generated_news_summary_is_explicitly_labeled(client):
    article = create_news(
        client,
        summary="Synthetic generated summary for the test.",
        summary_type="generated",
    )

    assert article["summary_type"] == "generated"
    assert article["original_url"] != article["summary"]


def test_news_import_requires_admin_token(client):
    response = client.post(
        "/api/news",
        json=create_sample_news(),
    )

    assert response.status_code == 401


def test_news_import_requires_configured_admin_token(client, monkeypatch):
    monkeypatch.delenv("AGROLENS_NEWS_ADMIN_TOKEN")

    response = client.post(
        "/api/news",
        json=create_sample_news(),
        headers={"X-News-Admin-Token": "test-news-token"},
    )

    assert response.status_code == 503


def test_news_import_rejects_duplicate_original_url(client):
    create_news(
        client,
        original_url=(
            "https://example.gov.in/news/agriculture-001?utm_source=feed"
        ),
    )

    response = client.post(
        "/api/news",
        json=create_sample_news(
            original_url=(
                "https://example.gov.in/news/agriculture-001"
                "?utm_campaign=another-feed"
            ),
        ),
        headers={"X-News-Admin-Token": "test-news-token"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "An article with this URL already exists."
    )


def test_news_can_be_filtered_by_category_and_region(client):
    create_news(client, category="markets", region="Karnataka")
    create_news(
        client,
        title="Tamil Nadu test article",
        category="weather",
        region="Tamil Nadu",
        original_url="https://example.gov.in/news/agriculture-002",
    )

    response = client.get(
        "/api/news",
        params={"category": "weather", "region": "Tamil Nadu"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["articles"][0]["category"] == "weather"
    assert response.json()["articles"][0]["region"] == "Tamil Nadu"


@pytest.mark.parametrize(
    "overrides",
    [
        {"summary": "Summary without a source marker"},
        {"summary_type": "unknown"},
        {"original_url": "not-a-url"},
        {"published_at": "not-a-timestamp"},
    ],
)
def test_news_import_rejects_invalid_article_data(client, overrides):
    response = client.post(
        "/api/news",
        json=create_sample_news(**overrides),
        headers={"X-News-Admin-Token": "test-news-token"},
    )

    assert response.status_code == 422


def test_news_update_rejects_duplicate_url_and_preserves_existing_article(client):
    first = create_news(client)
    create_news(
        client,
        title="Second synthetic article",
        original_url="https://example.gov.in/news/agriculture-002",
    )

    response = client.put(
        f"/api/news/{first['news_id']}",
        json=create_sample_news(
            original_url="https://example.gov.in/news/agriculture-002",
            title="Conflicting article",
        ),
        headers={"X-News-Admin-Token": "test-news-token"},
    )

    assert response.status_code == 409
    unchanged = client.get(f"/api/news/{first['news_id']}")
    assert unchanged.status_code == 200
    assert unchanged.json()["title"] == first["title"]


def test_news_detail_and_update_return_404_for_unknown_article(client):
    unknown_id = str(uuid4())

    detail = client.get(f"/api/news/{unknown_id}")
    update = client.put(
        f"/api/news/{unknown_id}",
        json=create_sample_news(),
        headers={"X-News-Admin-Token": "test-news-token"},
    )

    assert detail.status_code == 404
    assert update.status_code == 404


def test_mandi_sync_imports_provider_records_without_inventing_units(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "test-data-gov-key")
    calls = mock_mandi_provider(
        monkeypatch,
        [create_mandi_provider_record()],
    )

    response = client.post(
        "/api/mandi/sync",
        params={"offset": 0, "limit": 25},
        headers={"X-Mandi-Admin-Token": "test-mandi-token"},
    )

    assert response.status_code == 200
    assert response.json()["fetched"] == 1
    assert response.json()["inserted_or_updated"] == 1
    assert calls[0]["params"] == {
        "api-key": "test-data-gov-key",
        "offset": 0,
        "limit": 25,
    }

    prices = client.get(
        "/api/mandi/prices/latest",
        params={"commodity": "Tomato", "state": "Karnataka"},
    )
    assert prices.status_code == 200
    record = prices.json()["prices"][0]
    assert record["district"] == "Bengaluru Urban"
    assert record["minimum_price"] == 1800
    assert record["maximum_price"] == 2400
    assert record["modal_price"] == 2100
    assert record["price_unit"] is None
    assert record["data_source"] == "data.gov.in / AGMARKNET"


def test_import_national_mandi_csv_keeps_aggregates_separate_from_markets(
    client,
    tmp_path,
):
    csv_path = tmp_path / "national_mandi.csv"
    csv_path.write_text(
        "\n".join(
            [
                ",,,,Marketwise Price & Arrival Report (02-11-2026),,,,",
                ",,,Price (Rs./Quintal),,,Arrival (Metric Tonnes),,",
                (
                    "Commodity Group,Commodity,MSP (Rs./Quintal) 2026-27,"
                    '"Price on 02 Nov, 2026","Price on 01 Nov, 2026",'
                    '"Price on 31 Oct, 2026","Arrival on 02 Nov, 2026",'
                    '"Arrival on 01 Nov, 2026","Arrival on 31 Oct, 2026"'
                ),
                (
                    "Vegetables,Tomato,-,2075.15,2162.84,2148.65,"
                    "4749.50,1974.07,3056.23"
                ),
                (
                    "Vegetables,Onion,-,3616.74,4174.02,3253.53,"
                    "16479.04,1861.06,16263.47"
                ),
            ]
        ),
        encoding="utf-8",
    )

    imported = mandi_service.import_national_summary_csv(csv_path)

    assert imported == 6
    response = client.get(
        "/api/mandi/national/daily",
        params={"commodity": "Tomato"},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 3
    record = response.json()["summaries"][0]
    assert record["report_date"] == "2026-11-02"
    assert record["observation_date"] == "2026-11-02"
    assert record["price_rs_per_quintal"] == 2075.15
    assert record["arrival_metric_tonnes"] == 4749.5
    assert record["msp_rs_per_quintal"] is None
    assert record["data_source"] == "Marketwise Price & Arrival Report"

    market_prices = client.get("/api/mandi/prices/latest")
    assert market_prices.status_code == 200
    assert market_prices.json()["total"] == 0

    assert mandi_service.import_national_summary_csv(csv_path) == 6
    assert client.get("/api/mandi/national/daily").json()["total"] == 6


def test_national_mandi_csv_rejects_bad_rows_without_partial_storage(
    client,
    tmp_path,
):
    csv_path = tmp_path / "invalid_national_mandi.csv"
    csv_path.write_text(
        "\n".join(
            [
                ",,,,Marketwise Price & Arrival Report (02-11-2026),,,,",
                (
                    "Commodity Group,Commodity,MSP (Rs./Quintal) 2026-27,"
                    '"Price on 02 Nov, 2026","Price on 01 Nov, 2026",'
                    '"Price on 31 Oct, 2026","Arrival on 02 Nov, 2026",'
                    '"Arrival on 01 Nov, 2026","Arrival on 31 Oct, 2026"'
                ),
                (
                    "Vegetables,Tomato,-,2075.15,2162.84,2148.65,"
                    "4749.50,1974.07,3056.23"
                ),
                (
                    "Vegetables,Onion,-,invalid,4174.02,3253.53,"
                    "16479.04,1861.06,16263.47"
                ),
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(mandi_service.MandiServiceError) as error:
        mandi_service.import_national_summary_csv(csv_path)

    assert error.value.status_code == 422
    response = client.get("/api/mandi/national/daily")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_mandi_sync_requires_admin_token(client, monkeypatch):
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "test-data-gov-key")

    response = client.post("/api/mandi/sync")

    assert response.status_code == 401


def test_mandi_sync_requires_provider_api_key(client, monkeypatch):
    monkeypatch.delenv("AGROLENS_DATA_GOV_IN_API_KEY", raising=False)

    response = client.post(
        "/api/mandi/sync",
        headers={"X-Mandi-Admin-Token": "test-mandi-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Mandi data service is not configured."
    )


def test_mandi_sync_is_idempotent_for_same_market_observation(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "test-data-gov-key")
    calls = mock_mandi_provider(
        monkeypatch,
        [create_mandi_provider_record()],
    )
    headers = {"X-Mandi-Admin-Token": "test-mandi-token"}

    first_sync = client.post(
        "/api/mandi/sync",
        headers=headers,
    )
    second_sync = client.post(
        "/api/mandi/sync",
        headers=headers,
    )
    prices = client.get("/api/mandi/prices/history")

    assert first_sync.status_code == 200
    assert second_sync.status_code == 200
    assert len(calls) == 2
    assert prices.json()["total"] == 1


def test_mandi_history_filters_and_paginates(client, monkeypatch):
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "test-data-gov-key")
    mock_mandi_provider(
        monkeypatch,
        [
            create_mandi_provider_record(
                Arrival_Date="01/11/2026",
                Modal_Price="1800",
            ),
            create_mandi_provider_record(
                Arrival_Date="02/11/2026",
                Modal_Price="1900",
            ),
            create_mandi_provider_record(
                Market="Mysuru",
                District="Mysuru",
                Arrival_Date="02/11/2026",
                Modal_Price="2000",
            ),
        ],
    )
    sync = client.post(
        "/api/mandi/sync",
        headers={"X-Mandi-Admin-Token": "test-mandi-token"},
    )
    assert sync.status_code == 200

    response = client.get(
        "/api/mandi/prices/history",
        params={
            "commodity": "Tomato",
            "market": "Bengaluru",
            "start_date": "2026-11-01",
            "end_date": "2026-11-04",
            "limit": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["count"] == 1
    assert response.json()["prices"][0]["modal_price"] == 1900


def test_mandi_latest_prices_selects_most_recent_row_per_market(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "test-data-gov-key")
    mock_mandi_provider(
        monkeypatch,
        [
            create_mandi_provider_record(
                Arrival_Date="01/11/2026",
                Modal_Price="1800",
            ),
            create_mandi_provider_record(
                Arrival_Date="02/11/2026",
                Modal_Price="1900",
            ),
        ],
    )
    sync = client.post(
        "/api/mandi/sync",
        headers={"X-Mandi-Admin-Token": "test-mandi-token"},
    )
    assert sync.status_code == 200

    response = client.get(
        "/api/mandi/prices/latest",
        params={"commodity": "Tomato"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["prices"][0]["modal_price"] == 1900


def test_mandi_sync_rejects_malformed_provider_data_without_partial_storage(
    client,
    monkeypatch,
):
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "test-data-gov-key")
    mock_mandi_provider(
        monkeypatch,
        [
            create_mandi_provider_record(),
            create_mandi_provider_record(Arrival_Date="unknown"),
        ],
    )

    response = client.post(
        "/api/mandi/sync",
        headers={"X-Mandi-Admin-Token": "test-mandi-token"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "The mandi provider returned a record with invalid fields."
    )
    prices = client.get("/api/mandi/prices/history")
    assert prices.json()["total"] == 0


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/api/mandi/prices/latest", {"limit": 101}),
        ("/api/mandi/prices/history", {"start_date": "not-a-date"}),
        (
            "/api/mandi/prices/history",
            {"start_date": "2026-11-04", "end_date": "2026-11-03"},
        ),
    ],
)
def test_mandi_price_endpoints_validate_filters(client, path, params):
    response = client.get(path, params=params)

    assert response.status_code == 422


def test_mandi_provider_error_does_not_expose_api_key(client, monkeypatch):
    secret = "test-data-gov-key"
    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", secret)

    def fake_get(url, *, params, timeout):
        return SimpleNamespace(
            is_error=True,
            status_code=403,
            json=lambda: {},
        )

    monkeypatch.setattr(mandi_service.httpx, "get", fake_get)

    response = client.post(
        "/api/mandi/sync",
        headers={"X-Mandi-Admin-Token": "test-mandi-token"},
    )

    assert response.status_code == 503
    assert secret not in response.text

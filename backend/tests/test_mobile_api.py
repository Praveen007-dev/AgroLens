from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.app import database
from backend.app.main import app
from backend.app.services import auth as auth_service
from backend.app.services import mandi, weather


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "mobile-api.db")
    weather.clear_cache()
    with TestClient(app) as test_client:
        yield test_client
    weather.clear_cache()


def create_scan(scan_id="mobile-scan-001", **overrides):
    scan = {
        "scan_id": scan_id,
        "timestamp": "2026-11-05T08:30:00Z",
        "crop": "Tomato",
        "image_path": "file:///device/private/photos/tomato.jpg",
        "image_reference": None,
        "ai_prediction": {
            "prediction_id": "prediction-001",
            "crop": "Tomato",
            "disease_label": "Tomato___Early_blight",
            "confidence": 0.91,
            "top_predictions": [
                {"label": "Tomato___Early_blight", "confidence": 0.91},
                {"label": "Tomato___healthy", "confidence": 0.08},
            ],
            "is_low_confidence": False,
            "model_version": "mobile-model-v1",
            "inference_timestamp": "2026-11-05T08:29:59Z",
        },
        "farmer_feedback": None,
        "expert_verification": None,
        "location": {
            "latitude": 12.97,
            "longitude": 77.59,
            "region": "Karnataka",
            "has_consent": True,
        },
        "sync_status": "pending",
        "metadata": {"source": "mobile"},
    }
    scan.update(overrides)
    return scan


def register(client, **overrides):
    payload = {
        "username": "Anika_Rao",
        "email": "anika@example.com",
        "password": "Harvest2026",
    }
    payload.update(overrides)
    return client.post("/api/v1/auth/register", json=payload)


def test_health_aliases_and_v1_scan_create_and_read(client):
    assert client.get("/health").status_code == 200
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/v1/health").json()["status"] == "healthy"

    payload = create_scan()
    response = client.post(
        "/api/v1/scans",
        json=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Client-App": "AgroLens",
            "X-Client-Version": "0.1.0",
        },
    )
    assert response.status_code == 201
    assert response.json()["scan_id"] == payload["scan_id"]
    record = client.get("/api/v1/scans/mobile-scan-001")
    assert record.status_code == 200
    body = record.json()
    assert body["ai_prediction"]["disease_label"] == "Tomato___Early_blight"
    assert body["expert_verification"] is None
    assert body["location"]["latitude"] == 12.97
    assert body["image_path"] == payload["image_path"]


def test_scan_location_is_not_saved_without_consent(client):
    payload = create_scan(
        scan_id="no-location-consent",
        location={
            "latitude": 12.97,
            "longitude": 77.59,
            "region": "Karnataka",
            "has_consent": False,
        },
    )
    assert client.post("/api/v1/scans", json=payload).status_code == 201
    location = client.get("/api/v1/scans/no-location-consent").json()["location"]
    assert location == {
        "latitude": None,
        "longitude": None,
        "region": None,
        "has_consent": False,
    }


def test_scan_duplicate_id_is_idempotent_only_for_same_payload(client):
    payload = create_scan()
    assert client.post("/api/v1/scans", json=payload).status_code == 201
    replay = client.post("/api/v1/scans", json=payload)
    assert replay.status_code == 201
    assert replay.json()["scan_id"] == payload["scan_id"]
    assert client.get("/api/v1/scans?limit=20&offset=0").json()["total"] == 1
    conflict = client.post(
        "/api/v1/scans",
        json={
            **payload,
            "crop": "Potato",
            "ai_prediction": {**payload["ai_prediction"], "crop": "Potato"},
        },
    )
    assert conflict.status_code == 409
    conflict = client.post(
        "/api/v1/scans",
        json={
            **payload,
            "ai_prediction": {
                **payload["ai_prediction"],
                "disease_label": "Tomato___late_blight",
            },
        },
    )
    assert conflict.status_code == 409


def test_scan_replay_with_timezone_offsets_is_idempotent(client):
    payload = create_scan(
        scan_id="offset-timestamp-scan",
        timestamp="2026-11-05T11:00:00+05:30",
        ai_prediction={
            **create_scan()["ai_prediction"],
            "inference_timestamp": "2026-11-05T10:59:59+05:30",
        },
    )
    assert client.post("/api/v1/scans", json=payload).status_code == 201
    replay = client.post("/api/v1/scans", json=payload)
    assert replay.status_code == 201
    assert replay.json()["scan_id"] == payload["scan_id"]
    record = client.get("/api/v1/scans/offset-timestamp-scan").json()
    assert record["timestamp"] == "2026-11-05T05:30:00+00:00"
    assert record["ai_prediction"]["inference_timestamp"] == (
        "2026-11-05T05:29:59+00:00"
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"timestamp": "not-a-timestamp"},
        {"timestamp": "2026-11-05T08:30:00"},
        {
            "ai_prediction": {
                **create_scan()["ai_prediction"],
                "confidence": 1.1,
            }
        },
        {
            "ai_prediction": {
                **create_scan()["ai_prediction"],
                "inference_timestamp": "2026-11-05T08:29:59",
            }
        },
        {"crop": "Potato"},
    ],
)
def test_scan_validates_timestamps_confidence_and_crop(overrides, client):
    response = client.post("/api/v1/scans", json=create_scan(**overrides))
    assert response.status_code == 422


def test_scan_history_feedback_and_missing_scan(client):
    for index in range(3):
        assert client.post(
            "/api/v1/scans",
            json=create_scan(scan_id=f"scan-{index}"),
        ).status_code == 201

    history = client.get("/api/v1/scans?limit=2&offset=1")
    assert history.status_code == 200
    assert len(history.json()["items"]) == 2
    assert history.json()["total"] == 3
    assert client.get("/api/v1/scans?limit=0").status_code == 422
    assert client.get("/api/v1/scans/missing").status_code == 404

    feedback = {
        "is_confirmed": False,
        "corrected_label": "Tomato___healthy",
        "notes": "Manual visual review.",
        "submitted_at": "2026-11-05T09:00:00Z",
    }
    response = client.post(
        "/api/v1/scans/scan-0/feedback",
        json=feedback,
    )
    assert response.status_code == 204
    assert client.get("/api/v1/scans/scan-0").json()["farmer_feedback"] == feedback
    assert client.post(
        "/api/v1/scans/not-there/feedback",
        json=feedback,
    ).status_code == 404


def test_scan_batch_is_atomic_and_idempotent(client):
    first = create_scan("batch-1")
    second = create_scan("batch-2")
    response = client.post("/api/v1/scans/batch", json=[first, second])
    assert response.status_code == 200
    assert response.json() == {"synced_count": 2}
    replay = client.post("/api/v1/scans/batch", json=[first, second])
    assert replay.json() == {"synced_count": 2}
    conflicting_batch = client.post(
        "/api/v1/scans/batch",
        json=[
            create_scan("batch-3"),
            {**second, "image_path": "different-image-path"},
        ],
    )
    assert conflicting_batch.status_code == 409
    assert client.get("/api/v1/scans/batch-3").status_code == 404
    assert client.post("/api/v1/scans/batch", json=[]).status_code == 422


def test_registration_login_me_and_logout_use_revocable_opaque_sessions(client):
    response = register(client)
    assert response.status_code == 201
    session = response.json()
    token = session["access_token"]
    assert session["token_type"] == "Bearer"
    assert session["user"]["username"] == "anika_rao"
    assert session["user"]["email"] == "anika@example.com"
    assert "password" not in session
    assert "password_hash" not in session["user"]

    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/auth/me", headers=headers).json() == session["user"]
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401
    assert client.get("/api/v1/auth/me").status_code == 401


def test_registration_normalizes_and_rejects_duplicate_accounts(client):
    first = register(client)
    assert first.status_code == 201
    duplicate_email = register(
        client,
        username="different",
        email=" ANIKA@example.com ",
    )
    assert duplicate_email.status_code == 409
    duplicate_username = register(
        client,
        username=" anika_rao ",
        email="different@example.com",
    )
    assert duplicate_username.status_code == 409
    invalid = register(
        client,
        username="a!",
        email="invalid",
        password="short",
    )
    assert invalid.status_code == 422
    connection = database.get_connection()
    try:
        password_hash = connection.execute(
            "SELECT password_hash FROM auth_users WHERE username = 'anika_rao'"
        ).fetchone()["password_hash"]
    finally:
        connection.close()
    assert password_hash.startswith("$argon2id$")
    assert "Harvest2026" not in password_hash
    invalid_password = client.post(
        "/api/v1/auth/register",
        json={
            "username": "another_user",
            "email": "another@example.com",
            "password": "q7!",
        },
    )
    assert invalid_password.status_code == 422
    assert "q7!" not in invalid_password.text


def test_login_by_email_or_username_and_generic_failures(client):
    assert register(client).status_code == 201
    by_email = client.post(
        "/api/v1/auth/login",
        json={"identifier": "ANIKA@example.com", "password": "Harvest2026"},
    )
    by_username = client.post(
        "/api/auth/login",
        json={"identifier": "ANIKA_RAO", "password": "Harvest2026"},
    )
    bad_password = client.post(
        "/api/v1/auth/login",
        json={"identifier": "anika@example.com", "password": "WrongPass2026"},
    )
    bad_identifier = client.post(
        "/api/v1/auth/login",
        json={"identifier": "unknown@example.com", "password": "WrongPass2026"},
    )
    assert by_email.status_code == by_username.status_code == 200
    assert bad_password.status_code == bad_identifier.status_code == 401
    assert bad_password.json() == bad_identifier.json()


def test_password_reset_is_generic_single_use_and_revokes_sessions(
    client, monkeypatch
):
    session = register(client).json()
    sent_tokens = []
    monkeypatch.setenv("AGROLENS_SMTP_HOST", "smtp.example.test")
    monkeypatch.setenv("AGROLENS_SMTP_PORT", "465")
    monkeypatch.setenv("AGROLENS_SMTP_USERNAME", "mailer")
    monkeypatch.setenv("AGROLENS_SMTP_PASSWORD", "test-secret")
    monkeypatch.setenv("AGROLENS_AUTH_FROM_EMAIL", "no-reply@example.test")
    monkeypatch.setenv(
        "AGROLENS_AUTH_PUBLIC_BASE_URL", "https://mobile.example.test"
    )
    monkeypatch.setattr(
        auth_service,
        "_send_reset_email",
        lambda email, token, configuration: sent_tokens.append((email, token)),
    )

    known = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "anika@example.com"},
    )
    unknown = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "unknown@example.com"},
    )
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()
    assert sent_tokens[0][0] == "anika@example.com"
    assert "reset_token" not in known.text

    reset = client.post(
        "/api/v1/auth/reset-password",
        json={
            "reset_token": sent_tokens[0][1],
            "new_password": "NewHarvest2026",
        },
    )
    assert reset.status_code == 200
    assert client.post(
        "/api/v1/auth/reset-password",
        json={
            "reset_token": sent_tokens[0][1],
            "new_password": "AnotherHarvest2026",
        },
    ).status_code == 400
    assert client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {session['access_token']}"},
    ).status_code == 401
    assert client.post(
        "/api/v1/auth/login",
        json={"identifier": "anika_rao", "password": "NewHarvest2026"},
    ).status_code == 200


def test_password_reset_without_smtp_does_not_expose_token(client, monkeypatch):
    assert register(client).status_code == 201
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "anika@example.com"},
    )
    assert response.status_code == 200
    assert "reset_token" not in response.text
    connection = database.get_connection()
    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM auth_password_resets"
        ).fetchone()[0]
    finally:
        connection.close()
    assert count == 0


def test_expired_password_reset_and_session_credentials_are_rejected(
    client, monkeypatch
):
    session = register(client).json()
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    connection = database.get_connection()
    try:
        connection.execute(
            "UPDATE auth_sessions SET expires_at = '2000-01-01T00:00:00+00:00'"
        )
        connection.commit()
    finally:
        connection.close()
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401

    sent_tokens = []
    for key, value in {
        "AGROLENS_SMTP_HOST": "smtp.example.test",
        "AGROLENS_SMTP_USERNAME": "mailer",
        "AGROLENS_SMTP_PASSWORD": "test-secret",
        "AGROLENS_AUTH_FROM_EMAIL": "no-reply@example.test",
        "AGROLENS_AUTH_PUBLIC_BASE_URL": "https://mobile.example.test",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(
        auth_service,
        "_send_reset_email",
        lambda email, token, configuration: sent_tokens.append(token),
    )
    assert client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "anika@example.com"},
    ).status_code == 200
    connection = database.get_connection()
    try:
        connection.execute(
            "UPDATE auth_password_resets SET expires_at = '2000-01-01T00:00:00+00:00'"
        )
        connection.commit()
    finally:
        connection.close()
    assert client.post(
        "/api/v1/auth/reset-password",
        json={
            "reset_token": sent_tokens[0],
            "new_password": "NewHarvest2026",
        },
    ).status_code == 400


def test_forgot_password_rate_limit_is_enforced(client, monkeypatch):
    monkeypatch.setattr(auth_service, "RESET_ATTEMPT_LIMIT", 1)
    payload = {"email": "unknown@example.com"}
    assert client.post("/api/v1/auth/forgot-password", json=payload).status_code == 200
    assert client.post("/api/v1/auth/forgot-password", json=payload).status_code == 429


def test_change_password_revokes_other_sessions_and_checks_old_password(client):
    first = register(client).json()
    second = client.post(
        "/api/v1/auth/login",
        json={"identifier": "anika@example.com", "password": "Harvest2026"},
    ).json()
    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {first['access_token']}"},
        json={
            "current_password": "Harvest2026",
            "new_password": "NewHarvest2026",
        },
    )
    assert response.status_code == 200
    assert client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {first['access_token']}"},
    ).status_code == 200
    assert client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {second['access_token']}"},
    ).status_code == 401
    assert client.post(
        "/api/v1/auth/login",
        json={"identifier": "anika@example.com", "password": "Harvest2026"},
    ).status_code == 401
    assert client.post(
        "/api/v1/auth/login",
        json={"identifier": "anika@example.com", "password": "NewHarvest2026"},
    ).status_code == 200


def test_login_rate_limit_is_enforced(client, monkeypatch):
    assert register(client).status_code == 201
    monkeypatch.setattr(auth_service, "LOGIN_ATTEMPT_LIMIT", 1)
    payload = {"identifier": "anika@example.com", "password": "wrong"}
    assert client.post("/api/v1/auth/login", json=payload).status_code == 401
    assert client.post("/api/v1/auth/login", json=payload).status_code == 429


def test_agriculture_adapters_return_empty_or_provider_data_without_fabrication(
    client, monkeypatch
):
    schemes_list = client.get("/api/v1/schemes?category=unavailable")
    news_list = client.get("/api/v1/news?category=unavailable")
    prices = client.get("/api/v1/market/prices?commodity=Tomato")
    history = client.get("/api/v1/market/history?commodity=Tomato")
    forecast = client.get("/api/v1/market/forecast?commodity=Tomato")
    assert schemes_list.json()["items"] == []
    assert news_list.json()["items"] == []
    assert prices.json()["items"] == []
    assert history.json()["items"] == []
    assert forecast.json()["forecast_available"] is False
    assert forecast.json()["items"] == []
    assert client.get("/api/v1/market/prices").status_code == 422

    class FakeWeather:
        provider = "test-provider"
        retrieved_at = datetime(2026, 11, 5, tzinfo=timezone.utc)
        location = {"name": "Bengaluru"}
        current = type(
            "Current",
            (),
            {
                "temperature_c": 25.0,
                "precipitation_mm": 1.0,
                "humidity_percent": 60,
                "wind_kph": 12.0,
            },
        )()
        forecast = [
            type(
                "Forecast",
                (),
                {
                    "date": "2026-11-05",
                    "min_temperature_c": 18.0,
                    "max_temperature_c": 28.0,
                    "total_precipitation_mm": 2.0,
                    "chance_of_rain_percent": 40,
                    "max_wind_kph": 15.0,
                },
            )()
        ]
        alerts = []

    monkeypatch.setattr(weather, "get_forecast", lambda location, days: FakeWeather())
    weather_response = client.get(
        "/api/v1/weather?location=12.97,77.59"
    )
    assert weather_response.status_code == 200
    assert weather_response.json()["temperature_c"] == 25.0
    assert weather_response.json()["rain_probability_pct"] == 40
    assert weather_response.json()["advisory"] is None


def test_agriculture_adapters_map_existing_scheme_news_and_market_records(
    client, monkeypatch
):
    monkeypatch.setenv("AGROLENS_SCHEMES_ADMIN_TOKEN", "scheme-test-token")
    scheme = client.post(
        "/api/schemes",
        headers={"X-Schemes-Admin-Token": "scheme-test-token"},
        json={
            "scheme_name": "Tomato Grower Support",
            "government_level": "state",
            "state": "Karnataka",
            "category": "horticulture",
            "description": "Verified source details.",
            "eligibility": None,
            "benefits": None,
            "required_documents": None,
            "application_deadline": None,
            "official_url": None,
            "source_name": "Verified department",
            "source_url": "https://example.gov.in/schemes/tomato",
            "last_verified_at": "2026-11-05T08:00:00Z",
        },
    )
    assert scheme.status_code == 201
    scheme_result = client.get(
        "/api/v1/schemes?state=Karnataka&category=horticulture"
    ).json()["items"]
    assert len(scheme_result) == 1
    assert scheme_result[0]["name"] == "Tomato Grower Support"

    monkeypatch.setenv("AGROLENS_NEWS_ADMIN_TOKEN", "news-test-token")
    article = client.post(
        "/api/news",
        headers={"X-News-Admin-Token": "news-test-token"},
        json={
            "title": "Tomato growing update",
            "summary": "Official summary.",
            "summary_type": "source_provided",
            "source": "Agriculture Department",
            "published_at": "2026-11-05T08:00:00Z",
            "category": "horticulture",
            "region": "Karnataka",
            "original_url": "https://example.gov.in/news/tomato",
        },
    )
    assert article.status_code == 201
    news_items = client.get(
        "/api/v1/news?category=horticulture"
    ).json()["items"]
    assert len(news_items) == 1
    assert news_items[0]["summary"] == "Official summary."
    assert news_items[0]["original_url"] == "https://example.gov.in/news/tomato"

    monkeypatch.setenv("AGROLENS_DATA_GOV_IN_API_KEY", "test-data-key")
    monkeypatch.setenv("AGROLENS_MANDI_ADMIN_TOKEN", "mandi-test-token")
    monkeypatch.setattr(
        mandi.httpx,
        "get",
        lambda *args, **kwargs: SimpleNamespace(
            is_error=False,
            json=lambda: {
                "records": [
                    {
                        "State": "Karnataka",
                        "District": "Bengaluru Urban",
                        "Market": "Bengaluru",
                        "Commodity": "Tomato",
                        "Variety": "Local",
                        "Grade": "FAQ",
                        "Arrival_Date": "05/11/2026",
                        "Min_Price": "1800",
                        "Max_Price": "2400",
                        "Modal_Price": "2100",
                    }
                ]
            },
        ),
    )
    sync = client.post(
        "/api/mandi/sync?limit=1",
        headers={"X-Mandi-Admin-Token": "mandi-test-token"},
    )
    assert sync.status_code == 200
    market_items = client.get(
        "/api/v1/market/prices?commodity=Tomato&state=Karnataka"
    ).json()["items"]
    assert len(market_items) == 1
    assert market_items[0]["modal_price"] == 2100
    assert market_items[0]["currency"] == "INR"
    assert market_items[0]["unit"] is None


def test_cors_preflight_supports_flutter_web_origin(client):
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5000"

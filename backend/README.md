# AgroLens Backend

## Overview

AgroLens is a crop disease and pest detection application. The mobile application performs AI inference locally and submits scan records to this backend.

The backend validates, stores, retrieves, aggregates, and exports scan records for the research dashboard.

This is a hackathon prototype. It does not have a real integration with IIHR or any government agricultural department.

## Technology Stack

- Python
- FastAPI
- SQLite
- Pydantic
- REST APIs
- JSON
- Pytest

## Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   │   └── scan.py
│   ├── services/
│   └── utils/
├── tests/
│   └── test_api.py
├── requirements.txt
├── README.md
└── agrolens.db
```

## Local Setup

### 1. Create a virtual environment

From the repository root:

```powershell
python -m venv backend\venv
```

### 2. Activate the environment

```powershell
.\backend\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use:

```powershell
.\backend\venv\Scripts\activate.bat
```

### 3. Install dependencies

```powershell
python -m pip install -r backend\requirements.txt
```

### 4. Start the server

Run from the repository root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Backend base URL:

```text
http://127.0.0.1:8000
```

The mobile API base URL is `http://127.0.0.1:8000/api/v1` for local
development. Existing clients can continue using the original `/api/...`
routes. The versioned API adds `/health`, `/scans`, `/auth`, `/weather`,
`/schemes`, `/news`, and `/market/...`; the existing `/api/weather/current`,
`/api/weather/forecast`, `/api/mandi/...`, `/api/schemes`, and `/api/news`
routes remain available. On a device, replace `127.0.0.1` with the backend
computer's LAN address. Use HTTPS in deployments.

## API Documentation

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health`, `/api/health`, `/api/v1/health` | Health check |
| POST | `/api/scans` | Submit a scan record |
| GET | `/api/scans` | Retrieve scans with filters |
| GET | `/api/scans/{scan_id}` | Retrieve one scan |
| GET | `/api/analytics/summary` | Dashboard statistics |
| GET | `/api/export/scans?format=csv` | Export research data as CSV |
| GET | `/api/export/scans?format=json` | Export research data as JSON |
| GET | `/api/schemes` | List verified agriculture schemes |
| GET | `/api/schemes/{scheme_id}` | Retrieve one agriculture scheme |
| POST | `/api/schemes/agent/discover` | Check official scheme sources (admin token required) |
| POST | `/api/schemes` | Add a verified scheme (admin token required) |
| PUT | `/api/schemes/{scheme_id}` | Update a verified scheme (admin token required) |
| GET | `/api/weather/current?location=...` | Current weather for the supplied location |
| GET | `/api/weather/forecast?location=...&days=3` | Current weather, daily forecast, and provider alerts |
| GET | `/api/news` | List imported agriculture news articles |
| GET | `/api/news/{news_id}` | Retrieve one article |
| POST | `/api/news/agent/collect` | Collect releases from the official PIB agriculture page (admin token required) |
| POST | `/api/news` | Import an article (admin token required) |
| PUT | `/api/news/{news_id}` | Update an article (admin token required) |
| GET | `/api/mandi/prices/latest` | Latest imported prices per market/commodity |
| GET | `/api/mandi/prices/history` | Historical imported mandi prices |
| GET | `/api/mandi/national/daily` | National commodity price/arrival summaries |
| POST | `/api/mandi/sync` | Import one page from data.gov.in (admin token required) |

### Local secrets and provider configuration

The backend loads `backend/.env` automatically at startup. The file is ignored
by Git. Start with the tracked template:

```powershell
if (-not (Test-Path backend\.env)) {
    Copy-Item backend\.env.example backend\.env
}
```

Edit `backend\.env` locally and fill only the credentials you have obtained:

```dotenv
AGROLENS_WEATHERAPI_KEY=your_rotated_weatherapi_key
AGROLENS_DATA_GOV_IN_API_KEY=your_data_gov_in_api_key
AGROLENS_MANDI_ADMIN_TOKEN=your_private_mandi_admin_token
AGROLENS_SCHEMES_ADMIN_TOKEN=your_private_schemes_admin_token
AGROLENS_NEWS_ADMIN_TOKEN=your_private_news_admin_token
```

Never commit or share `backend/.env`. Environment variables already supplied
by the hosting environment take precedence over values in the file. Restart
the backend after changing credentials.

### Agriculture schemes

The schemes catalog is stored in the additive `agriculture_schemes` table.
Existing scan tables are unchanged. The catalog starts empty: no eligibility,
benefit amount, or deadline is pre-populated without a verified source.

List records with optional `government_level` (`central` or `state`) and
`state` filters. Pagination uses `limit` (1–100) and `offset` (0 or greater):

```text
http://127.0.0.1:8000/api/schemes?government_level=state&state=Karnataka
```

Scheme records require a source name, source URL, and `last_verified_at`.
Unavailable scheme details should be `null`; state-government records require
a state. Create and update operations require the
`X-Schemes-Admin-Token` header. Set `AGROLENS_SCHEMES_ADMIN_TOKEN` in
`backend/.env`.

Do not commit the token. If it is unset, scheme writes return `503`; a missing
or incorrect token returns `401`. Protect this token in deployment and use
HTTPS outside local development.

The deterministic schemes source agent checks a fixed list of six central/state
government pages: [myScheme](https://www.myscheme.gov.in/), the agriculture
department pages for Karnataka, Tamil Nadu, Kerala, Andhra Pradesh, and Punjab.
It does not use an AI model or provider API key. Read cached/live discovery
with:

```text
http://127.0.0.1:8000/api/schemes/agent/discover
```

An administrator can force a refresh with the schemes admin token:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/schemes/agent/discover `
  -Headers @{ "X-Schemes-Admin-Token" = "your_private_schemes_admin_token" }
```

The response contains retrieval status and time, page title, headings, and
same-site links whose text matches scheme-related terms. `content_status`
distinguishes detected scheme references, detected error pages, and pages with
no scheme references. For Tamil Nadu, the agent also reads scheme IDs and names
from the official department's data endpoint for Agriculture, Horticulture,
Agricultural Engineering, and Agri Marketing. `collection_status` reports
whether that catalog read completed, partially completed, or failed. These
names are unverified candidates; eligibility, benefits, documents, and
deadlines are not imported. Other sources currently provide metadata only.

Results are cached for 15 minutes; add `?refresh=true` to check immediately.
The agent never writes scheme records. Review any source manually and use the
admin create/update endpoints only after verifying the actual scheme details.
Pages can change, block automated requests, redirect elsewhere, or render
their listings with JavaScript, so an available page does not mean all scheme
information was extracted or verified. Redirects are reported rather than
followed.

### Weather

Weather data uses [WeatherAPI.com](https://www.weatherapi.com/docs/) when a
valid `AGROLENS_WEATHERAPI_KEY` is configured. If no key is configured or
WeatherAPI fails, the backend falls back to the public
[Open-Meteo API](https://open-meteo.com/en/docs) and its geocoding service.
Open-Meteo data requires no API key; provide attribution to Open-Meteo when
displaying its data. WeatherAPI failures and fallback use are reported in the
backend logs.

For example:

```text
http://127.0.0.1:8000/api/weather/current?location=12.97,77.59
http://127.0.0.1:8000/api/weather/forecast?location=12.97,77.59&days=3
```

`location` is required and may be a city or coordinates supported by the
provider. The application does not infer a device location: only send a
farmer's location when the user has granted location permission. Forecasts
support 1–14 days. Successful data is cached in process memory for 10 minutes;
failures are not cached. The response identifies the provider actually used.
Open-Meteo does not provide weather alerts through this integration, so alerts
are empty and snow probability is `null` when unavailable. No sample weather
data is substituted. Crop-specific agronomic recommendations are not generated
until verified local guidance is integrated.

### Agriculture news

The `agriculture_news` table and `/api/news` routes provide a curated,
admin-managed catalog. A deterministic collector reads the official PIB
[agriculture releases page](https://www.pib.gov.in/newsite/pmreleases.aspx?mincode=27&reg=48&lang=2),
then fetches and parses each PIB release page. Trigger a bounded collection
(up to the current page's 20 releases) with the news admin token:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/news/agent/collect?limit=20 `
  -Headers @{ "X-News-Admin-Token" = "your_private_news_admin_token" }
```

The result reports listed, imported, duplicate, and failed counts. Collection
does not follow redirects, uses only numeric release IDs from the fixed PIB
page, limits response sizes and request time, and stores the PIB title, date,
source URL, ministry article text, and source-provided summary label. Duplicate
URLs are skipped safely. The collector processes the current list page only;
it does not crawl arbitrary pages or follow links outside PIB. News feed
freshness depends on running collection again.

Article imports retain the original article URL, source, publication date,
category, and optional region. Summaries must be labeled as
`source_provided` or `generated`; no summary is stored when its origin is
unknown. Duplicate canonical article URLs return `409 Conflict`. List requests
support `category`, `region`, `limit`, and `offset`.

Configure a separate admin token for imports and updates by setting
`AGROLENS_NEWS_ADMIN_TOKEN` in `backend/.env`.

Do not commit the token. If it is unset, writes return `503`; a missing or
incorrect token returns `401`. Protect it in deployment and use HTTPS outside
local development.

### Mandi prices

The backend syncs pages from the official
[data.gov.in daily mandi-price resource](https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi),
whose observations are attributed to AGMARKNET. A data.gov.in API key and a
separate admin token are required; set `AGROLENS_DATA_GOV_IN_API_KEY` and
`AGROLENS_MANDI_ADMIN_TOKEN` in `backend/.env`.

An administrator imports a page using `POST /api/mandi/sync?offset=0&limit=100`.
The limit is capped at 1000 per request; advance the offset to import later
pages. Provider responses are validated and upserted into the additive
`mandi_prices` table. Synchronization is explicit; it does not fetch live data
on each mobile request. Existing API-key, paging, and source limitations
remain subject to the official data.gov.in resource contract. Invalid provider
records fail the entire page rather than being silently dropped.

Read latest prices, optionally filtered by `commodity`, `state`, `district`,
`market`, `variety`, and date bounds:

```text
http://127.0.0.1:8000/api/mandi/prices/latest?commodity=Tomato&state=Karnataka
http://127.0.0.1:8000/api/mandi/prices/history?commodity=Tomato&start_date=2026-11-01&end_date=2026-11-04
```

The official resource schema does not specify a price unit, so `price_unit`
is returned as `null`; the backend does not guess. Historical queries cover
only observations synchronized into the local database. No numerical forecast
endpoint is enabled yet: it will be integrated after the dedicated forecasting
module and its API contract are provided. No LLM-generated price predictions
are used.

#### National commodity report CSV

The downloaded “Market Wise Price Arrival” CSV is actually a national
commodity summary: it contains commodity group, commodity, MSP, daily
price-per-quintal, and arrival-in-metric-tonnes columns, but no state, district,
or market. It is imported into the separate
`national_mandi_daily_summaries` table and must not be interpreted as a
Karnataka or individual-market price. The API can read these rows at
`GET /api/mandi/national/daily`, optionally filtered by `commodity`,
`start_date`, and `end_date`. The report date and each observation date are
preserved; `-` values remain `null`. Reimporting the same report updates its
rows rather than duplicating them.

### Scan filters

The scan retrieval endpoint supports:

- `crop`
- `disease`
- `start_date`
- `end_date`
- `verification_status`
- `page`
- `limit`

Example:

```text
http://127.0.0.1:8000/api/scans?crop=Tomato&disease=Early%20Blight&page=1&limit=20
```

## Example Scan Submission

### Request

```json
{
  "crop": "Tomato",
  "scan_timestamp": "2026-11-04T09:30:00Z",
  "model_version": "AgroLens-Mobile-v1",
  "disease_label": "Early Blight",
  "confidence": 0.94,
  "image_ref": "sample-image-001",
  "farmer_confirmed_label": "Early Blight",
  "feedback_text": "The prediction looks correct.",
  "location_consent": false
}
```

### Response

```json
{
  "scan_id": "generated-uuid",
  "submission_status": "success",
  "message": "Scan record submitted successfully."
}
```

The backend generates a unique scan ID if one is not provided.

## Dashboard Summary Example

```json
{
  "total_scans": 2,
  "crop_counts": {
    "Tomato": 2
  },
  "disease_counts": {
    "Early Blight": 2
  },
  "verification_counts": {
    "pending": 2
  }
}
```

## Research Data Export

CSV export:

```text
http://127.0.0.1:8000/api/export/scans?format=csv
```

JSON export:

```text
http://127.0.0.1:8000/api/export/scans?format=json
```

Exports include selected research fields and exclude farmer feedback and location metadata.

## Database

SQLite is used for the hackathon prototype.

The database is initialized automatically when the FastAPI application starts.

The database file is:

```text
backend/agrolens.db
```

AI prediction, farmer feedback, expert verification, and optional metadata are stored separately.

Farmer feedback does not automatically mark a scan as expert verified.

Location data is optional and only included when location consent is provided.

## CORS Configuration

The backend allows local dashboard development from:

```text
http://localhost:3000
http://localhost:5173
```

These origins default in `app/config.py`; override them with
`AGROLENS_CORS_ORIGINS`.

## Running Tests

From the repository root:

```powershell
python -m pytest backend/tests/test_api.py -v
```

The API test suite covers scan submission and retrieval, validation, analytics, exports, schemes, weather, news, and mandi prices.

## Frontend Integration

The mobile application can submit scan records using:

```text
POST http://127.0.0.1:8000/api/scans
```

The research dashboard can retrieve data using:

```text
GET http://127.0.0.1:8000/api/scans
GET http://127.0.0.1:8000/api/analytics/summary
```

For a mobile device or another computer, `127.0.0.1` must be replaced with the backend computer's LAN IP address.

The versioned mobile scan contract below is available at
`/api/v1/scans`; the older scan API remains available at `/api/scans`.

## Mobile API v1

The Flutter client's mobile API base URL is:

```text
http://127.0.0.1:8000/api/v1
```

The mobile routes below are relative to that base URL:

| Method | Route | Notes |
|---|---|---|
| GET | `/health` | Health check |
| POST, GET | `/scans` | Create scan / paginated history |
| POST | `/scans/batch` | Atomic batch sync |
| GET | `/scans/{scan_id}` | Retrieve a scan |
| POST | `/scans/{scan_id}/feedback` | Create or replace farmer feedback |
| POST | `/auth/register`, `/auth/login` | Create account or start a session |
| POST | `/auth/forgot-password`, `/auth/reset-password` | Password reset |
| POST | `/auth/change-password`, `/auth/logout` | Authenticated session actions |
| GET | `/auth/me` | Authenticated profile |
| GET | `/weather`, `/schemes`, `/news` | Agriculture information |
| GET | `/market/prices`, `/market/history`, `/market/forecast` | Market data |

The existing `/api/...` endpoints remain unchanged. Versioned mobile names
intentionally differ from those legacy names (for example, `/weather` maps
the existing current-weather/forecast service and `/market/prices` maps
`/api/mandi/prices/latest`).

For Flutter Web, set `AGROLENS_CORS_ORIGINS` to a comma-separated list of
allowed browser origins. Local defaults include Flutter's common
`localhost:5000` and `localhost:7357` development ports. The API accepts
standard JSON requests and does not require `X-Client-App` or
`X-Client-Version`; those headers may be sent by clients.

### Scan history and feedback

`POST /scans` accepts a mobile inference record. The mobile app performs
inference locally; there is no disease-prediction endpoint. Example:

```json
{
  "scan_id": "unique-id",
  "timestamp": "2026-11-05T08:30:00Z",
  "crop": "Tomato",
  "image_path": "device-local-path",
  "image_reference": null,
  "ai_prediction": {
    "prediction_id": "prediction-id",
    "crop": "Tomato",
    "disease_label": "Tomato___Early_blight",
    "confidence": 0.91,
    "top_predictions": [
      {"label": "Tomato___Early_blight", "confidence": 0.91}
    ],
    "is_low_confidence": false,
    "model_version": "model-version",
    "inference_timestamp": "2026-11-05T08:29:59Z"
  },
  "farmer_feedback": null,
  "expert_verification": null,
  "location": {
    "latitude": 12.97,
    "longitude": 77.59,
    "region": "Karnataka",
    "has_consent": true
  },
  "sync_status": "pending",
  "metadata": null
}
```

`timestamp` and `inference_timestamp` must be ISO-8601 values with timezone.
Confidence values are in `[0, 1]`; the scan and prediction crop names must
match. Replaying an identical `scan_id` and payload is safe; reusing an ID
with different data returns `409`. `POST /scans/batch` accepts an array of
1–100 records and is atomic: a conflicting record rejects the whole batch.
`GET /scans?limit=20&offset=0` returns `{ "items": [...], "total": n, ... }`.
`GET /scans/{scan_id}` returns `404` for a missing record.

The server stores device `image_path` only as text metadata; it never opens or
uploads that path. Coordinates and region are stored and returned only when
`location.has_consent` is true. AI inference, farmer feedback, and expert
verification remain separate; receiving an AI result does not mark a scan
expert verified. `POST /scans/{scan_id}/feedback` replaces the scan's current
farmer feedback and returns `204`, or `404` when the scan is missing.

Scan and agriculture endpoints remain public for compatibility with the
current Flutter client, which does not yet send session credentials. Do not
rely on this API for per-user data isolation until the client and authorization
policy are coordinated.

### Username and password authentication

Local username/password auth is implemented under both `/api/v1/auth/...`
and the compatibility alias `/api/auth/...`. It is independent of scan and
agriculture routes:

- `POST /auth/register` with `{ "username", "email", "password" }`
- `POST /auth/login` with `{ "identifier", "password" }` where identifier is
  an email or username
- `GET /auth/me`
- `POST /auth/logout`
- `POST /auth/change-password`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`

Usernames are normalized to lowercase and must be 3–32 letters, digits, or
underscores. Emails are normalized to lowercase. Passwords must be 8–128
characters and contain at least one letter and one digit. Passwords are
hashed with Argon2id; plaintext passwords are not stored or returned.
Registration returns `201`, creates a session, and returns a basic user
profile. Duplicate usernames/emails return `409`; login failures return the
same generic `401` response.

Example registration response:

```json
{
  "access_token": "<opaque-session-token>",
  "token_type": "Bearer",
  "expires_at": "2026-12-05T08:30:00Z",
  "user": {
    "user_id": "<user-id>",
    "username": "farmer_01",
    "email": "farmer@example.com",
    "created_at": "2026-11-05T08:30:00Z"
  }
}
```

Send the returned token to authenticated endpoints:

```http
Authorization: Bearer <opaque-session-token>
```

Session credentials are random opaque bearer values. Only their SHA-256
digests are stored. Sessions expire after 30 days; there is no refresh-token
flow. Logout revokes the current session. Password reset invalidates all
sessions, and password change preserves the current session while revoking
other sessions. Rate limiting is persisted in SQLite: up to 10 login attempts
per identifier/IP in 15 minutes (and 50 per IP), and 5 reset requests per
email/IP per hour (and 20 per IP).

Password reset responses are generic whether or not an account exists. To
deliver reset tokens, configure `AGROLENS_SMTP_HOST`, `AGROLENS_SMTP_PORT`,
`AGROLENS_SMTP_USERNAME`, `AGROLENS_SMTP_PASSWORD`,
`AGROLENS_AUTH_FROM_EMAIL`, and `AGROLENS_AUTH_PUBLIC_BASE_URL`. Delivery uses
SMTP over TLS. Without this configuration no reset token is created or
exposed, and the endpoint still returns the generic response. OAuth is not
implemented: the current mobile client has no provider buttons or OAuth
exchange flow.

The current Flutter app still uses local-only auth. It must be separately
updated to call register/login, securely store the returned `access_token`,
send `Authorization: Bearer <access_token>` for `/auth/me`, logout, password changes,
and any future protected endpoints. The API does not require that token for
scan or agriculture endpoints at this stage.

### Agriculture data adapters

Versioned read adapters reuse the existing catalogs and provider services:

- `GET /weather?location=<place-or-latitude,longitude>&days=3` maps the
  existing provider result. `advisory` is sourced from provider alerts and
  remains `null` when no alert exists; unavailable weather returns the
  existing provider error rather than sample values.
- `GET /schemes?state=<state>&category=<category>` reads verified catalog
  records. Category is optional and `null` when not supplied; unavailable
  fields are not inferred.
- `GET /news?category=<category>` reads imported articles. Summaries remain
  distinct from `original_url`.
- `GET /market/prices?commodity=Tomato&state=Karnataka&district=...&market=...`
  and `GET /market/history?commodity=Tomato&market=...&days=30` read only
  locally synchronized mandi observations. Currency is `INR`; unit is `null`
  when not supplied by the official source.
- `GET /market/forecast?commodity=Tomato&market=...&days=5` currently returns
  `forecast_available: false` and an empty `items` list. No validated
  forecasting model is configured, so the backend does not fabricate
  estimates.

All list adapters return `{ "items": [...] }` with pagination metadata.

## Current Status

- FastAPI application implemented
- SQLite database initialized
- Scan validation implemented
- Scan submission implemented
- Scan retrieval implemented
- Dashboard summary implemented
- CSV export implemented
- JSON export implemented
- Automated API tests covering scan endpoints and integrated features
- API documentation available through Swagger UI

## Limitations

- Prototype database uses SQLite.
- Shared scan schema alignment is pending.
- No real IIHR or government department integration exists.
- Expert verification workflow is not yet implemented.
- Versioned username/password authentication uses local SQLite sessions; scan
  and agriculture endpoints are intentionally not user-protected yet.

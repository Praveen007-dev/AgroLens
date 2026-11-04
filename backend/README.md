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
| GET | `/api/health` | Health check |
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

These origins are configured in `app/main.py`.

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

The schema currently used is provisional and must be aligned with the shared project contract before final integration.

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
- Authentication and authorization are not yet implemented.

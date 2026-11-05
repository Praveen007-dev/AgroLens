
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from backend.app.config import get_cors_origins, get_cors_origin_regex
from backend.app.database import init_db, get_connection
from backend.app.routers.mandi import router as mandi_router
from backend.app.routers.auth import router as auth_router
from backend.app.routers.mobile import router as mobile_router
from backend.app.routers.news import router as news_router
from backend.app.routers.schemes import router as schemes_router
from backend.app.routers.weather import router as weather_router
from backend.app.schemas.scan import ScanCreate, ScanResponse

from datetime import datetime, timezone
from uuid import uuid4
import json
import csv
import io



app = FastAPI(
    title="AgroLens Backend API",
    summary="Backend services for AgroLens crop disease and pest detection research.",
    description="""
## AgroLens Backend API

AgroLens provides backend services for crop disease and pest scan research.

### Core capabilities
- Submit and store crop scan records
- Retrieve scans with filtering and pagination
- Access individual scan details
- View analytics and dashboard summaries
- Export research data in JSON and CSV formats
- Retrieve provider-backed weather observations and forecasts

### Data privacy
Research exports exclude farmer feedback and location metadata.
""",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "System",
            "description": "API health and system status."
        },
        {
            "name": "Scan Records",
            "description": "Create, retrieve, and filter crop scan records."
        },
        {
            "name": "Analytics",
            "description": "Research analytics and scan summary statistics."
        },
        {
            "name": "Research Data Export",
            "description": "Export selected research data as JSON or CSV."
        },
        {
            "name": "Weather",
            "description": "Retrieve provider-backed weather observations and forecasts."
        }
    ]
)

app.include_router(schemes_router)
app.include_router(weather_router)
app.include_router(news_router)
app.include_router(mandi_router)
app.include_router(mobile_router)
app.include_router(auth_router, prefix="/api")



# CORS configuration for local dashboard development
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=get_cors_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def auth_validation_exception_handler(
    request: Request,
    error: RequestValidationError,
):
    errors = error.errors()
    if request.url.path.startswith(("/api/v1/auth/", "/api/auth/")):
        errors = [
            {key: value for key, value in item.items() if key != "input"}
            for item in errors
        ]
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(errors)},
    )


@app.on_event("startup")
def startup_event():
    init_db()


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "AgroLens Backend"
    }


@app.get("/health", tags=["System"])
def root_health_check():
    return health_check()


# --------------------------------------------------
# SUBMIT SCAN
# --------------------------------------------------

@app.post("/api/scans", response_model=ScanResponse, status_code=201, tags=["Scan Records"])
def submit_scan(scan: ScanCreate):

    scan_id = scan.scan_id or str(uuid4())

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO scan_records (
                scan_id,
                crop,
                scan_timestamp,
                model_version,
                image_ref
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            scan_id,
            scan.crop,
            scan.scan_timestamp.isoformat(),
            scan.model_version,
            scan.image_ref
        ))

        cursor.execute("""
            INSERT INTO ai_predictions (
                scan_id,
                disease_label,
                confidence
            )
            VALUES (?, ?, ?)
        """, (
            scan_id,
            scan.disease_label,
            scan.confidence
        ))

        # Store farmer feedback separately
        if scan.farmer_confirmed_label or scan.feedback_text:
            cursor.execute("""
                INSERT INTO farmer_feedback (
                    scan_id,
                    farmer_confirmed_label,
                    feedback_text
                )
                VALUES (?, ?, ?)
            """, (
                scan_id,
                scan.farmer_confirmed_label,
                scan.feedback_text
            ))

        # Store optional metadata separately
        if (
            scan.location_consent
            or scan.environmental_data
            or scan.additional_metadata
        ):
            cursor.execute("""
                INSERT INTO optional_metadata (
                    scan_id,
                    location_consent,
                    latitude,
                    longitude,
                    environmental_data,
                    additional_metadata
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                scan_id,
                int(scan.location_consent),
                scan.latitude if scan.location_consent else None,
                scan.longitude if scan.location_consent else None,
                json.dumps(scan.environmental_data)
                    if scan.environmental_data else None,
                json.dumps(scan.additional_metadata)
                    if scan.additional_metadata else None
            ))

        connection.commit()

        return ScanResponse(
            scan_id=scan_id,
            submission_status="success",
            message="Scan record submitted successfully."
        )

    except Exception as error:
        connection.rollback()

        if "UNIQUE constraint failed" in str(error) or \
           "PRIMARY KEY" in str(error):
            raise HTTPException(
                status_code=409,
                detail="Scan ID already exists."
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to submit scan record."
        )

    finally:
        connection.close()


# --------------------------------------------------
# RETRIEVE SCANS WITH FILTERS
# --------------------------------------------------
@app.get(
    "/api/scans",
    tags=["Scan Records"],
    summary="Retrieve crop scan records",
    description="""
    Retrieve crop scan records with optional filtering and pagination.

    Filters:
    - crop: Filter by crop type
    - disease: Filter by detected disease
    - start_date: Filter records from this date
    - end_date: Filter records until this date
    - verification_status: Filter by verification status

    Pagination:
    - page: Page number (minimum 1)
    - limit: Records per page (1 to 100)
    """
)

def get_scans(
    crop: str | None = None,
    disease: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    verification_status: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    filters = []
    parameters = []

    if crop:
        filters.append("s.crop = ?")
        parameters.append(crop)

    if disease:
        filters.append("p.disease_label = ?")
        parameters.append(disease)

    if start_date:
        filters.append("s.scan_timestamp >= ?")
        parameters.append(start_date)

    if end_date:
        filters.append("s.scan_timestamp <= ?")
        parameters.append(end_date)

    if verification_status:
        filters.append("s.verification_status = ?")
        parameters.append(verification_status)

    where_clause = ""

    if filters:
        where_clause = " WHERE " + " AND ".join(filters)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Count all records matching the filters
        count_query = """
            SELECT COUNT(*) AS total
            FROM scan_records s
            JOIN ai_predictions p ON s.scan_id = p.scan_id
        """ + where_clause

        cursor.execute(count_query, parameters)
        total = cursor.fetchone()["total"]

        # Retrieve the requested page
        query = """
            SELECT
                s.scan_id,
                s.crop,
                s.scan_timestamp,
                s.model_version,
                s.verification_status,
                p.disease_label,
                p.confidence,
                om.latitude,
                om.longitude,
                om.location_consent
            FROM scan_records s
            JOIN ai_predictions p ON s.scan_id = p.scan_id
            LEFT JOIN optional_metadata om ON s.scan_id = om.scan_id
        """ + where_clause + """
            ORDER BY s.scan_timestamp DESC
            LIMIT ? OFFSET ?
        """

        paginated_parameters = parameters + [
            limit,
            (page - 1) * limit
        ]

        cursor.execute(query, paginated_parameters)

        scans = [dict(row) for row in cursor.fetchall()]

        total_pages = (total + limit - 1) // limit

        return {
            "page": page,
            "limit": limit,
            "count": len(scans),
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "scans": scans
        }

    finally:
        connection.close()


# --------------------------------------------------
# RETRIEVE ONE SCAN
# --------------------------------------------------
@app.get("/api/scans/{scan_id}", tags=["Scan Records"])
def get_scan(scan_id: str):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                s.scan_id,
                s.crop,
                s.scan_timestamp,
                s.model_version,
                s.image_ref,
                s.verification_status,
                p.disease_label,
                p.confidence
            FROM scan_records s
            JOIN ai_predictions p ON s.scan_id = p.scan_id
            WHERE s.scan_id = ?
        """, (scan_id,))

        scan = cursor.fetchone()
        if scan is None:
            raise HTTPException(
                status_code=404,
                detail="Scan record not found."
            )

        return dict(scan)

    finally:
        connection.close()


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------

@app.get("/api/analytics/summary", tags=["Analytics"])
def dashboard_summary():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total_scans
            FROM scan_records
        """)

        total_scans = cursor.fetchone()["total_scans"]

        cursor.execute("""
            SELECT crop, COUNT(*) AS count
            FROM scan_records
            GROUP BY crop
        """)

        crop_counts = {
            row["crop"]: row["count"]
            for row in cursor.fetchall()
        }

        cursor.execute("""
            SELECT disease_label, COUNT(*) AS count
            FROM ai_predictions
            GROUP BY disease_label
        """)

        disease_counts = {
            row["disease_label"]: row["count"]
            for row in cursor.fetchall()
        }

        cursor.execute("""
            SELECT verification_status, COUNT(*) AS count
            FROM scan_records
            GROUP BY verification_status
        """)

        verification_counts = {
            row["verification_status"]: row["count"]
            for row in cursor.fetchall()
        }

        return {
            "total_scans": total_scans,
            "crop_counts": crop_counts,
            "disease_counts": disease_counts,
            "verification_counts": verification_counts
        }

    finally:
        connection.close()


# --------------------------------------------------
# EXPORT RESEARCH DATA
# --------------------------------------------------

@app.get("/api/export/scans", tags=["Research Data Export"])
def export_scans(
    format: str = Query("json", pattern="^(csv|json)$")
):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Export only selected research fields.
        # Excludes personal feedback and location metadata.
        cursor.execute("""
            SELECT
                s.scan_id,
                s.crop,
                s.scan_timestamp,
                s.model_version,
                p.disease_label,
                p.confidence,
                s.verification_status
            FROM scan_records s
            JOIN ai_predictions p ON s.scan_id = p.scan_id
            ORDER BY s.scan_timestamp DESC
        """)

        rows = [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()

    if format == "json":
        return JSONResponse(content=rows)

    output = io.StringIO()

    fieldnames = [
        "scan_id",
        "crop",
        "scan_timestamp",
        "model_version",
        "disease_label",
        "confidence",
        "verification_status"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=agrolens_scans.csv"
        }
    )

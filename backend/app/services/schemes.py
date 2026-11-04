import json
import sqlite3
from uuid import uuid4

from backend.app import database
from backend.app.schemas.scheme import SchemeInput, SchemeRecord


def _record_from_row(row: sqlite3.Row) -> SchemeRecord:
    record = dict(row)
    record["required_documents"] = (
        json.loads(record["required_documents"])
        if record["required_documents"] is not None
        else None
    )
    return SchemeRecord.model_validate(record)


def list_schemes(
    government_level: str | None,
    state: str | None,
    limit: int,
    offset: int,
) -> tuple[list[SchemeRecord], int]:
    filters = []
    parameters = []

    if government_level is not None:
        filters.append("government_level = ?")
        parameters.append(government_level)
    if state is not None:
        filters.append("state = ?")
        parameters.append(state)

    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    connection = database.get_connection()
    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM agriculture_schemes" + where_clause,
            parameters,
        ).fetchone()[0]
        rows = connection.execute(
            "SELECT * FROM agriculture_schemes"
            + where_clause
            + " ORDER BY scheme_name COLLATE NOCASE LIMIT ? OFFSET ?",
            [*parameters, limit, offset],
        ).fetchall()
        return [_record_from_row(row) for row in rows], total
    finally:
        connection.close()


def get_scheme(scheme_id: str) -> SchemeRecord | None:
    connection = database.get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM agriculture_schemes WHERE scheme_id = ?",
            (scheme_id,),
        ).fetchone()
        return _record_from_row(row) if row is not None else None
    finally:
        connection.close()


def create_scheme(scheme: SchemeInput) -> SchemeRecord:
    scheme_id = str(uuid4())
    values = scheme.model_dump(mode="json")
    values["required_documents"] = (
        json.dumps(values["required_documents"])
        if values["required_documents"] is not None
        else None
    )

    connection = database.get_connection()
    try:
        connection.execute(
            """
            INSERT INTO agriculture_schemes (
                scheme_id, scheme_name, government_level, state,
                description, eligibility, benefits, required_documents,
                application_deadline, official_url, source_name, source_url,
                last_verified_at
            ) VALUES (
                :scheme_id, :scheme_name, :government_level, :state,
                :description, :eligibility, :benefits, :required_documents,
                :application_deadline, :official_url, :source_name, :source_url,
                :last_verified_at
            )
            """,
            {"scheme_id": scheme_id, **values},
        )
        connection.commit()
        row = connection.execute(
            "SELECT * FROM agriculture_schemes WHERE scheme_id = ?",
            (scheme_id,),
        ).fetchone()
        return _record_from_row(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_scheme(scheme_id: str, scheme: SchemeInput) -> SchemeRecord | None:
    values = scheme.model_dump(mode="json")
    values["required_documents"] = (
        json.dumps(values["required_documents"])
        if values["required_documents"] is not None
        else None
    )
    connection = database.get_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE agriculture_schemes SET
                scheme_name = :scheme_name,
                government_level = :government_level,
                state = :state,
                description = :description,
                eligibility = :eligibility,
                benefits = :benefits,
                required_documents = :required_documents,
                application_deadline = :application_deadline,
                official_url = :official_url,
                source_name = :source_name,
                source_url = :source_url,
                last_verified_at = :last_verified_at,
                updated_at = CURRENT_TIMESTAMP
            WHERE scheme_id = :scheme_id
            """,
            {**values, "scheme_id": scheme_id},
        )
        if cursor.rowcount == 0:
            return None
        connection.commit()
        row = connection.execute(
            "SELECT * FROM agriculture_schemes WHERE scheme_id = ?",
            (scheme_id,),
        ).fetchone()
        return _record_from_row(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

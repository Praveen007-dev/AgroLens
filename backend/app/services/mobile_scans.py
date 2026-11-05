import json
import sqlite3
from datetime import timezone

from backend.app import database
from backend.app.schemas.mobile import FarmerFeedback, MobileScanCreate


class DuplicateScanError(Exception):
    pass


class MobileScanStorageError(Exception):
    pass


def _dump(value) -> str | None:
    return value.model_dump_json() if value is not None else None


def _scan_payload(scan: MobileScanCreate) -> dict:
    location = scan.location
    has_consent = location.has_consent
    prediction = scan.ai_prediction.model_dump(mode="json")
    prediction["inference_timestamp"] = (
        scan.ai_prediction.inference_timestamp.astimezone(timezone.utc).isoformat()
    )
    return {
        "scan_id": scan.scan_id,
        "timestamp": scan.timestamp.astimezone(timezone.utc).isoformat(),
        "crop": scan.crop,
        "image_path": scan.image_path,
        "image_reference": scan.image_reference,
        "ai_prediction": prediction,
        "farmer_feedback": (
            scan.farmer_feedback.model_dump(mode="json")
            if scan.farmer_feedback
            else None
        ),
        "expert_verification": scan.expert_verification,
        "location": {
            "latitude": location.latitude if has_consent else None,
            "longitude": location.longitude if has_consent else None,
            "region": location.region if has_consent else None,
            "has_consent": has_consent,
        },
        "sync_status": scan.sync_status,
        "metadata": scan.metadata,
    }


def _store_scan(connection: sqlite3.Connection, scan: MobileScanCreate) -> bool:
    payload = _scan_payload(scan)
    existing = connection.execute(
        "SELECT * FROM scan_records WHERE scan_id = ?", (scan.scan_id,)
    ).fetchone()
    if existing is not None:
        existing_mobile = connection.execute(
            "SELECT * FROM mobile_scan_details WHERE scan_id = ?", (scan.scan_id,)
        ).fetchone()
        if existing_mobile is None:
            raise DuplicateScanError
        existing_prediction = connection.execute(
            "SELECT disease_label, confidence FROM ai_predictions WHERE scan_id = ?",
            (scan.scan_id,),
        ).fetchone()
        existing_payload = {
            "scan_id": scan.scan_id,
            "timestamp": existing["scan_timestamp"],
            "crop": existing["crop"],
            "image_path": existing_mobile["image_path"],
            "image_reference": existing_mobile["image_reference"],
            "ai_prediction": {
                "prediction_id": existing_mobile["prediction_id"],
                "crop": existing["crop"],
                "disease_label": existing_prediction["disease_label"],
                "confidence": existing_prediction["confidence"],
                "top_predictions": json.loads(existing_mobile["top_predictions"] or "[]"),
                "is_low_confidence": bool(existing_mobile["is_low_confidence"]),
                "model_version": existing["model_version"],
                "inference_timestamp": existing_mobile["inference_timestamp"],
            },
            "farmer_feedback": json.loads(existing_mobile["farmer_feedback"])
            if existing_mobile["farmer_feedback"]
            else None,
            "expert_verification": json.loads(existing_mobile["expert_verification"])
            if existing_mobile["expert_verification"]
            else None,
            "location": {
                "latitude": existing_mobile["latitude"],
                "longitude": existing_mobile["longitude"],
                "region": existing_mobile["location_region"],
                "has_consent": bool(existing_mobile["location_has_consent"]),
            },
            "sync_status": existing_mobile["sync_status"],
            "metadata": json.loads(existing_mobile["metadata"])
            if existing_mobile["metadata"]
            else None,
        }
        if existing_payload != payload:
            raise DuplicateScanError
        return False

    prediction = scan.ai_prediction
    location = scan.location
    has_consent = location.has_consent
    connection.execute(
        """
        INSERT INTO scan_records (
            scan_id, crop, scan_timestamp, model_version, image_ref
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            scan.scan_id,
            scan.crop,
            payload["timestamp"],
            prediction.model_version,
            scan.image_reference,
        ),
    )
    connection.execute(
        """
        INSERT INTO ai_predictions (scan_id, disease_label, confidence)
        VALUES (?, ?, ?)
        """,
        (scan.scan_id, prediction.disease_label, prediction.confidence),
    )
    if scan.farmer_feedback is not None:
        _store_feedback(connection, scan.scan_id, scan.farmer_feedback)
    connection.execute(
        """
        INSERT INTO mobile_scan_details (
            scan_id, image_path, image_reference, prediction_id,
            top_predictions, is_low_confidence, inference_timestamp,
            farmer_feedback, expert_verification, latitude, longitude,
            location_region, location_has_consent, sync_status, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            scan.scan_id,
            scan.image_path,
            scan.image_reference,
            prediction.prediction_id,
            json.dumps([item.model_dump(mode="json") for item in prediction.top_predictions]),
            int(prediction.is_low_confidence),
            prediction.inference_timestamp.astimezone(timezone.utc).isoformat(),
            _dump(scan.farmer_feedback),
            json.dumps(scan.expert_verification)
            if scan.expert_verification is not None
            else None,
            location.latitude if has_consent else None,
            location.longitude if has_consent else None,
            location.region if has_consent else None,
            int(has_consent),
            scan.sync_status,
            json.dumps(scan.metadata) if scan.metadata is not None else None,
        ),
    )
    return True


def _store_feedback(
    connection: sqlite3.Connection,
    scan_id: str,
    feedback: FarmerFeedback,
) -> None:
    connection.execute("DELETE FROM farmer_feedback WHERE scan_id = ?", (scan_id,))
    connection.execute(
        """
        INSERT INTO farmer_feedback (
            scan_id, farmer_confirmed_label, feedback_text, submitted_at
        ) VALUES (?, ?, ?, ?)
        """,
        (
            scan_id,
            feedback.corrected_label
            if not feedback.is_confirmed
            else None,
            feedback.notes,
            feedback.submitted_at.isoformat(),
        ),
    )


def save_scans(scans: list[MobileScanCreate]) -> int:
    connection = database.get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        inserted = 0
        for scan in scans:
            _store_scan(connection, scan)
            inserted += 1
        connection.commit()
        return inserted
    except DuplicateScanError:
        connection.rollback()
        raise
    except sqlite3.Error as error:
        connection.rollback()
        raise MobileScanStorageError from error
    finally:
        connection.close()


def _read_scan(connection: sqlite3.Connection, scan_id: str) -> dict | None:
    row = connection.execute(
        """
        SELECT s.*, p.disease_label, p.confidence,
               d.image_path, d.image_reference, d.prediction_id,
               d.top_predictions, d.is_low_confidence,
               d.inference_timestamp, d.farmer_feedback,
               d.expert_verification, d.latitude, d.longitude,
               d.location_region, d.location_has_consent,
               d.sync_status, d.metadata
        FROM scan_records s
        LEFT JOIN ai_predictions p ON p.scan_id = s.scan_id
        LEFT JOIN mobile_scan_details d ON d.scan_id = s.scan_id
        WHERE s.scan_id = ?
        """,
        (scan_id,),
    ).fetchone()
    if row is None:
        return None

    feedback = row["farmer_feedback"]
    expert = row["expert_verification"]
    metadata = row["metadata"]
    top_predictions = row["top_predictions"]
    has_details = row["prediction_id"] is not None
    return {
        "scan_id": row["scan_id"],
        "timestamp": row["scan_timestamp"],
        "crop": row["crop"],
        "image_path": row["image_path"] if has_details else None,
        "image_reference": (
            row["image_reference"] if has_details else row["image_ref"]
        ),
        "ai_prediction": {
            "prediction_id": row["prediction_id"] or row["scan_id"],
            "crop": row["crop"],
            "disease_label": row["disease_label"],
            "confidence": row["confidence"],
            "top_predictions": json.loads(top_predictions or "[]"),
            "is_low_confidence": bool(row["is_low_confidence"])
            if row["is_low_confidence"] is not None
            else None,
            "model_version": row["model_version"],
            "inference_timestamp": row["inference_timestamp"]
            or row["scan_timestamp"],
        },
        "farmer_feedback": json.loads(feedback) if feedback else None,
        "expert_verification": json.loads(expert) if expert else None,
        "location": {
            "latitude": row["latitude"] if row["location_has_consent"] else None,
            "longitude": row["longitude"] if row["location_has_consent"] else None,
            "region": row["location_region"]
            if row["location_has_consent"]
            else None,
            "has_consent": bool(row["location_has_consent"])
            if row["location_has_consent"] is not None
            else False,
        },
        "sync_status": row["sync_status"] or "synced",
        "metadata": json.loads(metadata) if metadata else None,
    }


def get_scan(scan_id: str) -> dict | None:
    connection = database.get_connection()
    try:
        return _read_scan(connection, scan_id)
    finally:
        connection.close()


def list_scans(limit: int, offset: int) -> tuple[list[dict], int]:
    connection = database.get_connection()
    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM scan_records"
        ).fetchone()[0]
        rows = connection.execute(
            "SELECT scan_id FROM scan_records "
            "ORDER BY scan_timestamp DESC, created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [
            _read_scan(connection, row["scan_id"])
            for row in rows
        ], total
    finally:
        connection.close()


def save_feedback(scan_id: str, feedback: FarmerFeedback) -> bool:
    connection = database.get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        exists = connection.execute(
            "SELECT 1 FROM scan_records WHERE scan_id = ?", (scan_id,)
        ).fetchone()
        if exists is None:
            connection.rollback()
            return False
        _store_feedback(connection, scan_id, feedback)
        connection.execute(
            """
            INSERT INTO mobile_scan_details (scan_id, farmer_feedback)
            VALUES (?, ?)
            ON CONFLICT(scan_id) DO UPDATE SET
                farmer_feedback = excluded.farmer_feedback
            """,
            (scan_id, feedback.model_dump_json()),
        )
        connection.commit()
        return True
    except sqlite3.Error as error:
        connection.rollback()
        raise MobileScanStorageError from error
    finally:
        connection.close()

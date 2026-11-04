import csv
import hashlib
import re
import sqlite3
import threading
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from backend.app import database
from backend.app.config import get_setting
from backend.app.schemas.mandi import (
    MandiPrice,
    NationalMandiDailySummary,
)


DATA_GOV_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_API_URL = (
    f"https://api.data.gov.in/resource/{DATA_GOV_RESOURCE_ID}"
)
DATA_SOURCE = "data.gov.in / AGMARKNET"
REQUEST_TIMEOUT_SECONDS = 20.0
MAX_SYNC_LIMIT = 1000
NATIONAL_CSV_SOURCE = "Marketwise Price & Arrival Report"

_sync_lock = threading.Lock()


class MandiServiceError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _national_optional_number(value: str) -> float | None:
    value = value.strip().replace(",", "")
    if not value or value == "-":
        return None
    try:
        number = float(value)
    except ValueError as error:
        raise ValueError("Invalid national mandi report number.") from error
    if number < 0:
        raise ValueError("National mandi report values cannot be negative.")
    return number


def _report_date(rows: list[list[str]]) -> date:
    for row in rows[:5]:
        for cell in row:
            match = re.search(
                r"Marketwise Price\s*&\s*Arrival Report\s*"
                r"\((\d{2}-\d{2}-\d{4})\)",
                cell,
                re.IGNORECASE,
            )
            if match:
                try:
                    return datetime.strptime(
                        match.group(1), "%d-%m-%Y"
                    ).date()
                except ValueError as error:
                    raise ValueError(
                        "Invalid report date in national mandi CSV."
                    ) from error
    raise ValueError("National mandi CSV is missing its report date.")


def import_national_summary_csv(
    csv_path: str | Path,
) -> int:
    path = Path(csv_path)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))
    except (OSError, UnicodeError, csv.Error) as error:
        raise MandiServiceError(
            422,
            "Unable to read the national mandi CSV file.",
        ) from error

    try:
        report_date = _report_date(rows)
        header_index = next(
            index
            for index, row in enumerate(rows)
            if len(row) >= 9
            and row[0].strip().casefold() == "commodity group"
            and row[1].strip().casefold() == "commodity"
        )
        headers = [header.strip() for header in rows[header_index]]
        if len(headers) != 9:
            raise ValueError("Unexpected national mandi CSV column count.")
        price_columns = {}
        arrival_columns = {}
        for index, header in enumerate(headers):
            price_match = re.fullmatch(
                r"Price on (\d{2} [A-Za-z]{3}, \d{4})",
                header,
                re.IGNORECASE,
            )
            arrival_match = re.fullmatch(
                r"Arrival on (\d{2} [A-Za-z]{3}, \d{4})",
                header,
                re.IGNORECASE,
            )
            if price_match:
                price_columns[datetime.strptime(
                    price_match.group(1), "%d %b, %Y"
                ).date()] = index
            if arrival_match:
                arrival_columns[datetime.strptime(
                    arrival_match.group(1), "%d %b, %Y"
                ).date()] = index
        if not price_columns or set(price_columns) != set(arrival_columns):
            raise ValueError(
                "National mandi CSV price and arrival date columns do not match."
            )

        msp_year_match = re.search(r"(\d{4}-\d{2})", headers[2])
        msp_year = msp_year_match.group(1) if msp_year_match else None
        retrieved_at = datetime.now(timezone.utc)
        summaries = []
        seen_records = set()
        for row in rows[header_index + 1:]:
            if not row or not any(cell.strip() for cell in row):
                continue
            if len(row) != len(headers):
                raise ValueError(
                    "National mandi CSV contains a malformed data row."
                )
            commodity_group = row[0].strip()
            commodity = row[1].strip()
            if not commodity_group or not commodity:
                raise ValueError(
                    "National mandi CSV contains a row without commodity data."
                )
            msp = _national_optional_number(row[2])
            for observation_date, price_index in price_columns.items():
                price = _national_optional_number(row[price_index])
                arrival = _national_optional_number(
                    row[arrival_columns[observation_date]]
                )
                if price is None and arrival is None:
                    continue
                identity = (
                    report_date.isoformat(),
                    commodity.casefold(),
                    observation_date.isoformat(),
                )
                if identity in seen_records:
                    raise ValueError(
                        "National mandi CSV contains duplicate commodity dates."
                    )
                seen_records.add(identity)
                summary_id = hashlib.sha256(
                    "\x1f".join(identity).encode("utf-8")
                ).hexdigest()
                summaries.append(
                    NationalMandiDailySummary(
                        summary_id=summary_id,
                        report_date=report_date,
                        commodity_group=commodity_group,
                        commodity=commodity,
                        msp_year=msp_year,
                        msp_rs_per_quintal=msp,
                        observation_date=observation_date,
                        price_rs_per_quintal=price,
                        arrival_metric_tonnes=arrival,
                        data_source=NATIONAL_CSV_SOURCE,
                        retrieved_at=retrieved_at,
                    )
                )
        if not summaries:
            raise ValueError("National mandi CSV contains no observations.")
    except (StopIteration, TypeError, ValueError) as error:
        raise MandiServiceError(
            422,
            "The national mandi CSV has an unsupported or invalid format.",
        ) from error

    connection = database.get_connection()
    try:
        connection.executemany(
            """
            INSERT INTO national_mandi_daily_summaries (
                summary_id, report_date, commodity_group, commodity,
                msp_year, msp_rs_per_quintal, observation_date,
                price_rs_per_quintal, arrival_metric_tonnes,
                data_source, retrieved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(report_date, commodity, observation_date) DO UPDATE SET
                commodity_group = excluded.commodity_group,
                msp_year = excluded.msp_year,
                msp_rs_per_quintal = excluded.msp_rs_per_quintal,
                price_rs_per_quintal = excluded.price_rs_per_quintal,
                arrival_metric_tonnes = excluded.arrival_metric_tonnes,
                data_source = excluded.data_source,
                retrieved_at = excluded.retrieved_at
            """,
            [
                (
                    item.summary_id,
                    item.report_date.isoformat(),
                    item.commodity_group,
                    item.commodity,
                    item.msp_year,
                    item.msp_rs_per_quintal,
                    item.observation_date.isoformat(),
                    item.price_rs_per_quintal,
                    item.arrival_metric_tonnes,
                    item.data_source,
                    item.retrieved_at.isoformat(),
                )
                for item in summaries
            ],
        )
        connection.commit()
    except sqlite3.Error as error:
        connection.rollback()
        raise MandiServiceError(
            500,
            "Failed to store national mandi summaries.",
        ) from error
    finally:
        connection.close()

    return len(summaries)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text and text.casefold() not in {"na", "n/a", "null"} else None


def _required_text(record: dict[str, Any], field: str) -> str:
    value = _optional_text(record.get(field))
    if value is None:
        raise ValueError(f"Missing required mandi field: {field}")
    return value


def _optional_price(record: dict[str, Any], field: str) -> float | None:
    value = _optional_text(record.get(field))
    if value is None:
        return None
    try:
        price = float(value.replace(",", ""))
    except ValueError as error:
        raise ValueError(f"Invalid numeric mandi field: {field}") from error
    if price < 0:
        raise ValueError(f"Negative mandi price in field: {field}")
    return price


def _arrival_date(value: str) -> date:
    for date_format in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue
    raise ValueError("Invalid mandi arrival date")


def _normalize_record(
    record: dict[str, Any],
    retrieved_at: datetime,
) -> MandiPrice:
    state = _required_text(record, "State")
    district = _required_text(record, "District")
    market = _required_text(record, "Market")
    commodity = _required_text(record, "Commodity")
    variety = _optional_text(record.get("Variety"))
    grade = _optional_text(record.get("Grade"))
    arrival_date = _arrival_date(_required_text(record, "Arrival_Date"))

    identity = "\x1f".join(
        value.casefold() if value is not None else ""
        for value in (
            state,
            district,
            market,
            commodity,
            variety,
            grade,
            arrival_date.isoformat(),
        )
    )
    price_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()

    return MandiPrice(
        price_id=price_id,
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
        arrival_date=arrival_date,
        minimum_price=_optional_price(record, "Min_Price"),
        maximum_price=_optional_price(record, "Max_Price"),
        modal_price=_optional_price(record, "Modal_Price"),
        price_unit=None,
        data_source=DATA_SOURCE,
        retrieved_at=retrieved_at,
    )


def _fetch_page(offset: int, limit: int, api_key: str) -> list[dict[str, Any]]:
    try:
        response = httpx.get(
            DATA_GOV_API_URL,
            params={
                "api-key": api_key,
                "offset": offset,
                "limit": limit,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException as error:
        raise MandiServiceError(
            504,
            "The mandi data provider did not respond before the timeout.",
        ) from error
    except httpx.RequestError as error:
        raise MandiServiceError(
            502,
            "Unable to connect to the mandi data provider.",
        ) from error

    if response.is_error:
        if response.status_code in (401, 403):
            raise MandiServiceError(
                503,
                "Mandi data provider credentials were rejected.",
            )
        raise MandiServiceError(
            502,
            "The mandi data provider returned an error.",
        )

    try:
        payload = response.json()
    except ValueError as error:
        raise MandiServiceError(
            502,
            "The mandi data provider returned invalid JSON.",
        ) from error

    if not isinstance(payload, dict) or not isinstance(
        payload.get("records"), list
    ):
        raise MandiServiceError(
            502,
            "The mandi provider response did not contain a records list.",
        )
    records = payload["records"]
    if len(records) > limit or any(
        not isinstance(record, dict) for record in records
    ):
        raise MandiServiceError(
            502,
            "The mandi provider response had an invalid records structure.",
        )
    return records


def sync_prices(offset: int, limit: int) -> int:
    api_key = get_setting("AGROLENS_DATA_GOV_IN_API_KEY")
    if not api_key:
        raise MandiServiceError(
            503,
            "Mandi data service is not configured.",
        )
    if limit > MAX_SYNC_LIMIT:
        raise MandiServiceError(
            422,
            f"limit must not exceed {MAX_SYNC_LIMIT}.",
        )
    if not _sync_lock.acquire(blocking=False):
        raise MandiServiceError(
            409,
            "A mandi data synchronization is already in progress.",
        )

    retrieved_at = datetime.now(timezone.utc)
    try:
        provider_records = _fetch_page(offset, limit, api_key)
        try:
            prices = [
                _normalize_record(record, retrieved_at)
                for record in provider_records
            ]
        except (TypeError, ValueError) as error:
            raise MandiServiceError(
                502,
                "The mandi provider returned a record with invalid fields.",
            ) from error

        connection = database.get_connection()
        try:
            connection.executemany(
                """
                INSERT INTO mandi_prices (
                    price_id, record_key, state, district, market, commodity,
                    variety, grade, arrival_date, minimum_price,
                    maximum_price, modal_price, price_unit, data_source,
                    retrieved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_key) DO UPDATE SET
                    minimum_price = excluded.minimum_price,
                    maximum_price = excluded.maximum_price,
                    modal_price = excluded.modal_price,
                    price_unit = excluded.price_unit,
                    data_source = excluded.data_source,
                    retrieved_at = excluded.retrieved_at
                """,
                [
                    (
                        price.price_id,
                        price.price_id,
                        price.state,
                        price.district,
                        price.market,
                        price.commodity,
                        price.variety,
                        price.grade,
                        price.arrival_date.isoformat(),
                        price.minimum_price,
                        price.maximum_price,
                        price.modal_price,
                        price.price_unit,
                        price.data_source,
                        price.retrieved_at.isoformat(),
                    )
                    for price in prices
                ],
            )
            connection.commit()
        except sqlite3.Error as error:
            connection.rollback()
            raise MandiServiceError(
                500,
                "Failed to store mandi price records.",
            ) from error
        finally:
            connection.close()

        return len(prices)
    finally:
        _sync_lock.release()


def list_national_summaries(
    commodity: str | None,
    start_date: date | None,
    end_date: date | None,
    limit: int,
    offset: int,
) -> tuple[list[NationalMandiDailySummary], int]:
    filters = []
    parameters: list[Any] = []
    if commodity is not None:
        filters.append("commodity = ?")
        parameters.append(commodity)
    if start_date is not None:
        filters.append("observation_date >= ?")
        parameters.append(start_date.isoformat())
    if end_date is not None:
        filters.append("observation_date <= ?")
        parameters.append(end_date.isoformat())
    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""

    connection = database.get_connection()
    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM national_mandi_daily_summaries" + where_clause,
            parameters,
        ).fetchone()[0]
        rows = connection.execute(
            "SELECT * FROM national_mandi_daily_summaries"
            + where_clause
            + " ORDER BY observation_date DESC, commodity COLLATE NOCASE"
            + " LIMIT ? OFFSET ?",
            [*parameters, limit, offset],
        ).fetchall()
        return [
            NationalMandiDailySummary(
                summary_id=row["summary_id"],
                report_date=date.fromisoformat(row["report_date"]),
                commodity_group=row["commodity_group"],
                commodity=row["commodity"],
                msp_year=row["msp_year"],
                msp_rs_per_quintal=row["msp_rs_per_quintal"],
                observation_date=date.fromisoformat(row["observation_date"]),
                price_rs_per_quintal=row["price_rs_per_quintal"],
                arrival_metric_tonnes=row["arrival_metric_tonnes"],
                data_source=row["data_source"],
                retrieved_at=datetime.fromisoformat(row["retrieved_at"]),
            )
            for row in rows
        ], total
    finally:
        connection.close()


def list_prices(
    commodity: str | None,
    state: str | None,
    district: str | None,
    market: str | None,
    variety: str | None,
    start_date: date | None,
    end_date: date | None,
    latest_only: bool,
    limit: int,
    offset: int,
) -> tuple[list[MandiPrice], int]:
    filters = []
    parameters: list[Any] = []
    for column, value in (
        ("commodity", commodity),
        ("state", state),
        ("district", district),
        ("market", market),
        ("variety", variety),
    ):
        if value is not None:
            filters.append(f"{column} = ?")
            parameters.append(value)
    if start_date is not None:
        filters.append("arrival_date >= ?")
        parameters.append(start_date.isoformat())
    if end_date is not None:
        filters.append("arrival_date <= ?")
        parameters.append(end_date.isoformat())

    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    connection = database.get_connection()
    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM mandi_prices" + where_clause,
            parameters,
        ).fetchone()[0]

        if latest_only:
            total = connection.execute(
                """
                SELECT COUNT(*) FROM (
                    SELECT 1 FROM mandi_prices
                """
                + where_clause
                + """
                    GROUP BY state, district, market, commodity,
                             COALESCE(variety, ''), COALESCE(grade, '')
                )
                """,
                parameters,
            ).fetchone()[0]
            latest_query = """
                SELECT p.* FROM mandi_prices p
                JOIN (
                    SELECT state, district, market, commodity,
                           COALESCE(variety, '') AS variety_key,
                           COALESCE(grade, '') AS grade_key,
                           MAX(arrival_date) AS latest_date
                    FROM mandi_prices
            """ + where_clause + """
                    GROUP BY state, district, market, commodity,
                             COALESCE(variety, ''), COALESCE(grade, '')
                ) latest
                ON p.state = latest.state
                AND p.district = latest.district
                AND p.market = latest.market
                AND p.commodity = latest.commodity
                AND COALESCE(p.variety, '') = latest.variety_key
                AND COALESCE(p.grade, '') = latest.grade_key
                AND p.arrival_date = latest.latest_date
            """
            rows = connection.execute(
                latest_query
                + " ORDER BY p.arrival_date DESC, p.commodity, p.market"
                + " LIMIT ? OFFSET ?",
                [*parameters, limit, offset],
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM mandi_prices"
                + where_clause
                + " ORDER BY arrival_date DESC, commodity, market"
                + " LIMIT ? OFFSET ?",
                [*parameters, limit, offset],
            ).fetchall()

        return [
            MandiPrice(
                price_id=row["price_id"],
                state=row["state"],
                district=row["district"],
                market=row["market"],
                commodity=row["commodity"],
                variety=row["variety"],
                grade=row["grade"],
                arrival_date=date.fromisoformat(row["arrival_date"]),
                minimum_price=row["minimum_price"],
                maximum_price=row["maximum_price"],
                modal_price=row["modal_price"],
                price_unit=row["price_unit"],
                data_source=row["data_source"],
                retrieved_at=datetime.fromisoformat(row["retrieved_at"]),
            )
            for row in rows
        ], total
    finally:
        connection.close()

import sqlite3
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import uuid4

from backend.app import database
from backend.app.schemas.news import NewsInput, NewsRecord


TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid"}


class DuplicateArticleError(Exception):
    pass


def canonicalize_article_url(url: str) -> str:
    parts = urlsplit(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.casefold() not in TRACKING_QUERY_KEYS
        and not key.casefold().startswith(TRACKING_QUERY_PREFIXES)
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parts.scheme.casefold(),
            parts.netloc.casefold(),
            path,
            urlencode(sorted(query)),
            "",
        )
    )


def _record_from_row(row: sqlite3.Row) -> NewsRecord:
    record = dict(row)
    record.pop("canonical_url")
    return NewsRecord.model_validate(record)


def list_news(
    category: str | None,
    region: str | None,
    limit: int,
    offset: int,
) -> tuple[list[NewsRecord], int]:
    filters = []
    parameters = []
    if category is not None:
        filters.append("category = ?")
        parameters.append(category)
    if region is not None:
        filters.append("region = ?")
        parameters.append(region)

    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    connection = database.get_connection()
    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM agriculture_news" + where_clause,
            parameters,
        ).fetchone()[0]
        rows = connection.execute(
            """
            SELECT * FROM agriculture_news
            """
            + where_clause
            + """
            ORDER BY published_at DESC, created_at DESC
            LIMIT ? OFFSET ?
            """,
            [*parameters, limit, offset],
        ).fetchall()
        return [_record_from_row(row) for row in rows], total
    finally:
        connection.close()


def get_article(news_id: str) -> NewsRecord | None:
    connection = database.get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM agriculture_news WHERE news_id = ?",
            (news_id,),
        ).fetchone()
        return _record_from_row(row) if row is not None else None
    finally:
        connection.close()


def get_article_by_url(url: str) -> NewsRecord | None:
    canonical_url = canonicalize_article_url(url)
    connection = database.get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM agriculture_news WHERE canonical_url = ?",
            (canonical_url,),
        ).fetchone()
        return _record_from_row(row) if row is not None else None
    finally:
        connection.close()


def create_article(article: NewsInput) -> NewsRecord:
    news_id = str(uuid4())
    values = article.model_dump(mode="json")
    values["original_url"] = str(article.original_url)
    canonical_url = canonicalize_article_url(values["original_url"])
    connection = database.get_connection()
    try:
        connection.execute(
            """
            INSERT INTO agriculture_news (
                news_id, title, summary, summary_type, source, published_at,
                category, region, original_url, canonical_url
            ) VALUES (
                :news_id, :title, :summary, :summary_type, :source,
                :published_at, :category, :region, :original_url,
                :canonical_url
            )
            """,
            {
                "news_id": news_id,
                **values,
                "canonical_url": canonical_url,
            },
        )
        connection.commit()
        row = connection.execute(
            "SELECT * FROM agriculture_news WHERE news_id = ?",
            (news_id,),
        ).fetchone()
        return _record_from_row(row)
    except sqlite3.IntegrityError as error:
        connection.rollback()
        if "canonical_url" in str(error):
            raise DuplicateArticleError from error
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_article(news_id: str, article: NewsInput) -> NewsRecord | None:
    values = article.model_dump(mode="json")
    values["original_url"] = str(article.original_url)
    values["canonical_url"] = canonicalize_article_url(values["original_url"])
    connection = database.get_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE agriculture_news SET
                title = :title,
                summary = :summary,
                summary_type = :summary_type,
                source = :source,
                published_at = :published_at,
                category = :category,
                region = :region,
                original_url = :original_url,
                canonical_url = :canonical_url,
                updated_at = CURRENT_TIMESTAMP
            WHERE news_id = :news_id
            """,
            {**values, "news_id": news_id},
        )
        if cursor.rowcount == 0:
            return None
        connection.commit()
        row = connection.execute(
            "SELECT * FROM agriculture_news WHERE news_id = ?",
            (news_id,),
        ).fetchone()
        return _record_from_row(row)
    except sqlite3.IntegrityError as error:
        connection.rollback()
        if "canonical_url" in str(error):
            raise DuplicateArticleError from error
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

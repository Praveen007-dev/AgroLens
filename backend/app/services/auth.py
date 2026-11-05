import hashlib
import logging
import re
import secrets
import smtplib
import sqlite3
import ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from uuid import uuid4

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from backend.app import database
from backend.app.config import get_setting
from backend.app.schemas.mobile import (
    AuthCredentials,
    AuthLogin,
    BasicUserProfile,
)


SESSION_TTL = timedelta(days=30)
RESET_TTL = timedelta(minutes=30)
LOGIN_WINDOW = timedelta(minutes=15)
RESET_WINDOW = timedelta(hours=1)
LOGIN_ATTEMPT_LIMIT = 10
RESET_ATTEMPT_LIMIT = 5
_logger = logging.getLogger(__name__)
_password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


class AuthServiceError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_username(username: str) -> str:
    return username.strip().lower()


def _valid_email(email: str) -> bool:
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",
            email,
        )
    ) and ".." not in email


def _valid_username(username: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9_]{3,32}", username))


def _valid_password(password: str) -> bool:
    return (
        8 <= len(password) <= 128
        and any(char.isalpha() for char in password)
        and any(char.isdigit() for char in password)
    )


def _profile(row: sqlite3.Row) -> BasicUserProfile:
    created_at = datetime.fromisoformat(row["created_at"])
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return BasicUserProfile(
        user_id=row["user_id"],
        username=row["username"],
        email=row["email"],
        created_at=created_at,
    )


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _rate_limit_key(action: str, subject: str, client_ip: str) -> str:
    digest = hashlib.sha256(
        f"{action}\x1f{subject.casefold()}\x1f{client_ip}".encode("utf-8")
    ).hexdigest()
    return f"{action}:{digest}"


def _check_rate_limit(
    action: str,
    subject: str,
    client_ip: str,
    *,
    window: timedelta,
    limit: int,
) -> None:
    key = _rate_limit_key(action, subject, client_ip)
    now = _now()
    cutoff = (now - timedelta(days=1)).isoformat()
    connection = database.get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "DELETE FROM auth_rate_limits WHERE window_started_at < ?",
            (cutoff,),
        )
        row = connection.execute(
            "SELECT window_started_at, attempt_count FROM auth_rate_limits "
            "WHERE bucket_key = ?",
            (key,),
        ).fetchone()
        if row is None:
            connection.execute(
                "INSERT INTO auth_rate_limits "
                "(bucket_key, window_started_at, attempt_count) VALUES (?, ?, 1)",
                (key, now.isoformat()),
            )
        else:
            started_at = datetime.fromisoformat(row["window_started_at"])
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            if now - started_at >= window:
                connection.execute(
                    "UPDATE auth_rate_limits SET window_started_at = ?, "
                    "attempt_count = 1 WHERE bucket_key = ?",
                    (now.isoformat(), key),
                )
            elif row["attempt_count"] >= limit:
                raise AuthServiceError(
                    429,
                    "Too many attempts. Please try again later.",
                )
            else:
                connection.execute(
                    "UPDATE auth_rate_limits SET attempt_count = attempt_count + 1 "
                    "WHERE bucket_key = ?",
                    (key,),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _issue_session(user_id: str) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = _now() + SESSION_TTL
    connection = database.get_connection()
    try:
        connection.execute(
            "DELETE FROM auth_sessions WHERE expires_at <= ?",
            (_now().isoformat(),),
        )
        connection.execute(
            "INSERT INTO auth_sessions "
            "(token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (_token_hash(token), user_id, _now().isoformat(), expires_at.isoformat()),
        )
        connection.commit()
    finally:
        connection.close()
    return token, expires_at


def _session_response(row: sqlite3.Row):
    from backend.app.schemas.mobile import AuthSessionResponse

    token, expires_at = _issue_session(row["user_id"])
    return AuthSessionResponse(
        access_token=token,
        expires_at=expires_at,
        user=_profile(row),
    )


def register(credentials: AuthCredentials):
    username = _normalize_username(credentials.username)
    email = _normalize_email(credentials.email)
    if not _valid_username(username):
        raise AuthServiceError(
            422,
            "Username must be 3–32 characters using letters, numbers, or underscores.",
        )
    if not _valid_email(email):
        raise AuthServiceError(422, "Enter a valid email address.")
    if not _valid_password(credentials.password):
        raise AuthServiceError(
            422,
            "Password must be 8–128 characters and contain a letter and a number.",
        )

    user_id = str(uuid4())
    password_hash = _password_hasher.hash(credentials.password)
    connection = database.get_connection()
    try:
        connection.execute(
            "INSERT INTO auth_users (user_id, username, email, password_hash) "
            "VALUES (?, ?, ?, ?)",
            (user_id, username, email, password_hash),
        )
        connection.commit()
        row = connection.execute(
            "SELECT * FROM auth_users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return _session_response(row)
    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise AuthServiceError(
            409,
            "An account with that username or email already exists.",
        ) from error
    finally:
        connection.close()


def login(credentials: AuthLogin, client_ip: str):
    identifier = credentials.identifier.strip().casefold()
    _check_rate_limit(
        "login",
        identifier,
        client_ip,
        window=LOGIN_WINDOW,
        limit=LOGIN_ATTEMPT_LIMIT,
    )
    _check_rate_limit(
        "login-ip",
        "",
        client_ip,
        window=LOGIN_WINDOW,
        limit=50,
    )
    connection = database.get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM auth_users WHERE email = ? COLLATE NOCASE "
            "OR username = ? COLLATE NOCASE",
            (identifier, identifier),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        _password_hasher.hash(credentials.password)
        raise AuthServiceError(401, "Invalid username/email or password.")
    try:
        _password_hasher.verify(row["password_hash"], credentials.password)
    except (VerifyMismatchError, VerificationError, InvalidHashError) as error:
        raise AuthServiceError(
            401, "Invalid username/email or password."
        ) from error
    return _session_response(row)


def authenticate_token(token: str | None) -> BasicUserProfile:
    if not token:
        raise AuthServiceError(401, "A valid session is required.")
    now = _now().isoformat()
    connection = database.get_connection()
    try:
        row = connection.execute(
            """
            SELECT u.* FROM auth_sessions s
            JOIN auth_users u ON u.user_id = s.user_id
            WHERE s.token_hash = ? AND s.expires_at > ?
            """,
            (_token_hash(token), now),
        ).fetchone()
        if row is None:
            raise AuthServiceError(401, "A valid session is required.")
        return _profile(row)
    finally:
        connection.close()


def logout(token: str) -> None:
    connection = database.get_connection()
    try:
        connection.execute(
            "DELETE FROM auth_sessions WHERE token_hash = ?", (_token_hash(token),)
        )
        connection.commit()
    finally:
        connection.close()


def change_password(
    user_id: str,
    current_password: str,
    new_password: str,
    current_token: str,
) -> None:
    if current_password == new_password:
        raise AuthServiceError(
            422, "New password must be different from the current password."
        )
    if not _valid_password(new_password):
        raise AuthServiceError(
            422,
            "Password must be 8–128 characters and contain a letter and a number.",
        )
    connection = database.get_connection()
    try:
        row = connection.execute(
            "SELECT password_hash FROM auth_users WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row is None:
            raise AuthServiceError(401, "A valid session is required.")
        try:
            _password_hasher.verify(row["password_hash"], current_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError) as error:
            raise AuthServiceError(401, "Current password is incorrect.") from error
        connection.execute(
            "UPDATE auth_users SET password_hash = ? WHERE user_id = ?",
            (_password_hasher.hash(new_password), user_id),
        )
        connection.execute(
            "DELETE FROM auth_sessions WHERE user_id = ? AND token_hash != ?",
            (user_id, _token_hash(current_token)),
        )
        connection.execute(
            "DELETE FROM auth_password_resets WHERE user_id = ?", (user_id,)
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _smtp_configuration() -> tuple[str, int, str, str, str, str] | None:
    host = get_setting("AGROLENS_SMTP_HOST")
    username = get_setting("AGROLENS_SMTP_USERNAME")
    password = get_setting("AGROLENS_SMTP_PASSWORD")
    sender = get_setting("AGROLENS_AUTH_FROM_EMAIL")
    public_url = get_setting("AGROLENS_AUTH_PUBLIC_BASE_URL")
    if not all((host, username, password, sender, public_url)):
        return None
    try:
        port = int(get_setting("AGROLENS_SMTP_PORT") or "465")
    except ValueError:
        return None
    return host, port, username, password, sender, public_url.rstrip("/")


def _send_reset_email(
    email: str,
    token: str,
    configuration: tuple[str, int, str, str, str, str],
) -> None:
    host, port, username, password, sender, public_url = configuration
    message = EmailMessage()
    message["Subject"] = "AgroLens password reset"
    message["From"] = sender
    message["To"] = email
    message.set_content(
        "Use this single-use AgroLens password reset token within 30 minutes:\n\n"
        f"{token}\n\n"
        f"Reset page: {public_url}/reset-password?token={token}\n\n"
        "If you did not request this, you can ignore this message."
    )
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context, timeout=10) as server:
        server.login(username, password)
        server.send_message(message)


def request_password_reset(email: str, client_ip: str) -> None:
    normalized_email = _normalize_email(email)
    _check_rate_limit(
        "password-reset",
        normalized_email,
        client_ip,
        window=RESET_WINDOW,
        limit=RESET_ATTEMPT_LIMIT,
    )
    _check_rate_limit(
        "password-reset-ip",
        "",
        client_ip,
        window=RESET_WINDOW,
        limit=20,
    )
    if not _valid_email(normalized_email):
        return
    configuration = _smtp_configuration()
    if configuration is None:
        _logger.warning("Password reset email is not configured.")
        return

    connection = database.get_connection()
    try:
        connection.execute(
            "DELETE FROM auth_password_resets "
            "WHERE expires_at <= ? OR used_at IS NOT NULL",
            (_now().isoformat(),),
        )
        row = connection.execute(
            "SELECT user_id FROM auth_users WHERE email = ? COLLATE NOCASE",
            (normalized_email,),
        ).fetchone()
        if row is None:
            return
        token = secrets.token_urlsafe(32)
        created_at = _now()
        connection.execute(
            "DELETE FROM auth_password_resets WHERE user_id = ?", (row["user_id"],)
        )
        connection.execute(
            "INSERT INTO auth_password_resets "
            "(token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (
                _token_hash(token),
                row["user_id"],
                created_at.isoformat(),
                (created_at + RESET_TTL).isoformat(),
            ),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    try:
        _send_reset_email(normalized_email, token, configuration)
    except (OSError, smtplib.SMTPException):
        _logger.exception("Could not deliver a password reset email.")
        connection = database.get_connection()
        try:
            connection.execute(
                "DELETE FROM auth_password_resets WHERE token_hash = ?",
                (_token_hash(token),),
            )
            connection.commit()
        finally:
            connection.close()


def reset_password(reset_token: str, new_password: str) -> None:
    if not _valid_password(new_password):
        raise AuthServiceError(
            422,
            "Password must be 8–128 characters and contain a letter and a number.",
        )
    token_digest = _token_hash(reset_token)
    now = _now()
    connection = database.get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT user_id FROM auth_password_resets "
            "WHERE token_hash = ? AND used_at IS NULL AND expires_at > ?",
            (token_digest, now.isoformat()),
        ).fetchone()
        if row is None:
            raise AuthServiceError(400, "Reset token is invalid or expired.")
        connection.execute(
            "UPDATE auth_users SET password_hash = ? WHERE user_id = ?",
            (_password_hasher.hash(new_password), row["user_id"]),
        )
        connection.execute(
            "UPDATE auth_password_resets SET used_at = ? WHERE token_hash = ?",
            (now.isoformat(), token_digest),
        )
        connection.execute(
            "DELETE FROM auth_sessions WHERE user_id = ?", (row["user_id"],)
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

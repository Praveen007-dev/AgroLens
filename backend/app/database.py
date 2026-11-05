
import sqlite3
from pathlib import Path

# Database file path
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "agrolens.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    """
    Initialize the AgroLens database and create tables.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # 1. Main scan records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_records (
                scan_id TEXT PRIMARY KEY,
                crop TEXT NOT NULL,
                scan_timestamp TEXT NOT NULL,
                model_version TEXT NOT NULL,
                image_ref TEXT,
                verification_status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (verification_status IN (
                        'pending', 'verified', 'rejected'
                    )),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. AI predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL UNIQUE,
                disease_label TEXT NOT NULL,
                confidence REAL NOT NULL
                    CHECK (confidence >= 0 AND confidence <= 1),
                FOREIGN KEY (scan_id)
                    REFERENCES scan_records(scan_id)
                    ON DELETE CASCADE
            )
        """)

        # 3. Farmer feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmer_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL,
                farmer_confirmed_label TEXT,
                feedback_text TEXT,
                submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id)
                    REFERENCES scan_records(scan_id)
                    ON DELETE CASCADE
            )
        """)

        # 4. Expert verification table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_verifications (
                verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL UNIQUE,
                expert_label TEXT,
                expert_notes TEXT,
                expert_reference TEXT,
                verified_at TEXT,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'verified', 'rejected')),
                FOREIGN KEY (scan_id)
                    REFERENCES scan_records(scan_id)
                    ON DELETE CASCADE
            )
        """)

        # 5. Optional metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optional_metadata (
                metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL UNIQUE,
                location_consent INTEGER NOT NULL DEFAULT 0
                    CHECK (location_consent IN (0, 1)),
                latitude REAL,
                longitude REAL,
                environmental_data TEXT,
                additional_metadata TEXT,
                FOREIGN KEY (scan_id)
                    REFERENCES scan_records(scan_id)
                    ON DELETE CASCADE
            )
        """)

        # Indexes for faster filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scan_crop
            ON scan_records(crop)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scan_timestamp
            ON scan_records(scan_timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scan_verification
            ON scan_records(verification_status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prediction_disease
            ON ai_predictions(disease_label)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agriculture_schemes (
                scheme_id TEXT PRIMARY KEY,
                scheme_name TEXT NOT NULL,
                government_level TEXT NOT NULL
                    CHECK (government_level IN ('central', 'state')),
                state TEXT,
                description TEXT,
                eligibility TEXT,
                benefits TEXT,
                required_documents TEXT,
                application_deadline TEXT,
                official_url TEXT,
                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL,
                last_verified_at TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK (government_level != 'state' OR state IS NOT NULL)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_schemes_level_state
            ON agriculture_schemes(government_level, state)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_schemes_name
            ON agriculture_schemes(scheme_name)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agriculture_news (
                news_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                summary_type TEXT
                    CHECK (summary_type IN ('source_provided', 'generated')
                        OR summary_type IS NULL),
                source TEXT NOT NULL,
                published_at TEXT,
                category TEXT NOT NULL,
                region TEXT,
                original_url TEXT NOT NULL,
                canonical_url TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK (
                    (summary IS NULL AND summary_type IS NULL)
                    OR (summary IS NOT NULL AND summary_type IS NOT NULL)
                )
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agriculture_news_published
            ON agriculture_news(published_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agriculture_news_category_region
            ON agriculture_news(category, region)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mandi_prices (
                price_id TEXT PRIMARY KEY,
                record_key TEXT NOT NULL UNIQUE,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                market TEXT NOT NULL,
                commodity TEXT NOT NULL,
                variety TEXT,
                grade TEXT,
                arrival_date TEXT NOT NULL,
                minimum_price REAL,
                maximum_price REAL,
                modal_price REAL,
                price_unit TEXT,
                data_source TEXT NOT NULL,
                retrieved_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mandi_prices_commodity_date
            ON mandi_prices(commodity, arrival_date DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mandi_prices_market_date
            ON mandi_prices(state, district, market, arrival_date DESC)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS national_mandi_daily_summaries (
                summary_id TEXT PRIMARY KEY,
                report_date TEXT NOT NULL,
                commodity_group TEXT NOT NULL,
                commodity TEXT NOT NULL,
                msp_year TEXT,
                msp_rs_per_quintal REAL,
                observation_date TEXT NOT NULL,
                price_rs_per_quintal REAL,
                arrival_metric_tonnes REAL,
                data_source TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                UNIQUE(report_date, commodity, observation_date)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_national_mandi_commodity_date
            ON national_mandi_daily_summaries(commodity, observation_date DESC)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mobile_scan_details (
                scan_id TEXT PRIMARY KEY,
                image_path TEXT,
                image_reference TEXT,
                prediction_id TEXT,
                top_predictions TEXT,
                is_low_confidence INTEGER,
                inference_timestamp TEXT,
                farmer_feedback TEXT,
                expert_verification TEXT,
                latitude REAL,
                longitude REAL,
                location_region TEXT,
                location_has_consent INTEGER NOT NULL DEFAULT 0
                    CHECK (location_has_consent IN (0, 1)),
                sync_status TEXT NOT NULL DEFAULT 'pending',
                metadata TEXT,
                FOREIGN KEY (scan_id)
                    REFERENCES scan_records(scan_id)
                    ON DELETE CASCADE
            )
        """)
        mobile_detail_columns = {
            row["name"]
            for row in cursor.execute(
                "PRAGMA table_info(mobile_scan_details)"
            ).fetchall()
        }
        for column in ("latitude", "longitude"):
            if column not in mobile_detail_columns:
                cursor.execute(
                    f"ALTER TABLE mobile_scan_details ADD COLUMN {column} REAL"
                )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES auth_users(user_id)
                    ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_sessions_user
            ON auth_sessions(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_sessions_expiry
            ON auth_sessions(expires_at)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_password_resets (
                token_hash TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                FOREIGN KEY (user_id)
                    REFERENCES auth_users(user_id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_rate_limits (
                bucket_key TEXT PRIMARY KEY,
                window_started_at TEXT NOT NULL,
                attempt_count INTEGER NOT NULL
            )
        """)

        scheme_columns = {
            row["name"]
            for row in cursor.execute(
                "PRAGMA table_info(agriculture_schemes)"
            ).fetchall()
        }
        if "category" not in scheme_columns:
            cursor.execute(
                "ALTER TABLE agriculture_schemes ADD COLUMN category TEXT"
            )

        connection.commit()

        print("AgroLens database initialized successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    init_db()

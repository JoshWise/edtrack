# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv

# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
#     future=True,
# )
# SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Optional: load .env in local dev
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except Exception:
    pass

# Try Streamlit secrets first (works both locally with .streamlit/secrets.toml and on Streamlit Cloud)
DB_URL = None
try:
    import streamlit as st  # streamlit is already in your stack
    if hasattr(st, "secrets"):
        # support both common keys
        DB_URL = st.secrets.get("DATABASE_URL") or st.secrets.get("SQLALCHEMY_DATABASE_URL")
except Exception:
    # streamlit isn't always importable (e.g., during Alembic/CLI); ignore
    pass

# Fall back to environment variables
DB_URL = DB_URL or os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")

# Final fallback: local SQLite file (safe for dev)
if not DB_URL:
    # Choose one behavior: EITHER hard-fail with an explicit error...
    # raise RuntimeError("No database URL found. Set DATABASE_URL (or SQLALCHEMY_DATABASE_URL) in env or Streamlit secrets.")
    # ...OR default to a local sqlite db for development:
    DB_URL = "sqlite:///./edtrack.db"

# Guard: SQLAlchemy requires a string/URL, not None/Path/etc.
if not isinstance(DB_URL, str) or not DB_URL.strip():
    raise RuntimeError(f"Invalid DATABASE_URL value: {repr(DB_URL)}")

# Example URL formats:
#   Postgres: postgresql+psycopg2://user:pass@host:5432/dbname
#   SQLite file: sqlite:///./edtrack.db
#   SQLite memory: sqlite:///:memory:

engine = create_engine(
    DB_URL,
    # For SQLite only, enable check_same_thread False when used with many frameworks:
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

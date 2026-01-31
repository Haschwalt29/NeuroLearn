import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    
    # Handle database URL for PostgreSQL (Render, etc.)
    database_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.abspath('aitutor.db')}")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Render Postgres (external hostname) requires SSL. Add sslmode if not present.
    if database_url.startswith("postgresql://") and "sslmode" not in database_url:
        database_url += "&sslmode=require" if "?" in database_url else "?sslmode=require"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SSL for Postgres; connect_timeout avoids long hangs on connection failure
    _pg_connect_args = {}
    if database_url.startswith("postgresql://"):
        _pg_connect_args = {"sslmode": "require", "connect_timeout": "10"}
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": _pg_connect_args,
    }
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config(name: str):
    mapping = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return mapping.get(name, DevelopmentConfig)



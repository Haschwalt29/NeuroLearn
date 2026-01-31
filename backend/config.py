import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    
    # Handle database URL for PostgreSQL (Render, etc.)
    database_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.abspath('aitutor.db')}")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # On Render, fromDatabase.connectionString is the *internal* URL (private network).
    # Do not force SSL for internal connections — it can cause "SSL connection closed unexpectedly".
    # For external Postgres (e.g. non-Render or manual external URL), require SSL.
    on_render = os.environ.get("RENDER") == "true"
    if (
        database_url.startswith("postgresql://")
        and not on_render
        and "sslmode" not in database_url
    ):
        database_url += "&sslmode=require" if "?" in database_url else "?sslmode=require"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Prevent stale DB connections; only force SSL when not on Render (external URLs)
    _pg_connect_args = {"sslmode": "require"} if (
        database_url.startswith("postgresql://") and not on_render
    ) else {}
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
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



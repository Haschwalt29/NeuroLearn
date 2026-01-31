import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    
    # Handle database URL with SSL for PostgreSQL on Render
    database_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.abspath('aitutor.db')}")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    if database_url.startswith("postgresql://") and "sslmode" not in database_url:
        # Render Postgres requires SSL; append without breaking existing query params
        database_url += "&sslmode=require" if "?" in database_url else "?sslmode=require"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Prevent stale DB connections on managed providers; SSL for Render Postgres
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require"} if database_url.startswith("postgresql://") else {},
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



import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    
    # Handle database URL with SSL for PostgreSQL on Render
    database_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.abspath('aitutor.db')}")
    if database_url.startswith("postgres://"):
        # Convert postgres:// to postgresql:// and add SSL mode
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        # Add SSL mode if not already present
        if "sslmode" not in database_url:
            database_url += "?sslmode=require"
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
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



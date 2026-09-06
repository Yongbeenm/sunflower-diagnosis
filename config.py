import os
from urllib.parse import quote_plus


def _normalize_database_url(url: str, *, env_name: str) -> str:
    value = str(url or "").strip()
    if value.startswith("mysql://"):
        value = value.replace("mysql://", "mysql+pymysql://", 1)
    if "://" not in value:
        raise RuntimeError(
            f"{env_name} must be a valid SQLAlchemy URL, got: {value or '<empty>'}"
        )
    return value


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "doctor-sunflower-secret")

    # Keep project paths available for any local file storage needs.
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    SQLITE_DB_PATH = os.path.join(INSTANCE_DIR, "doctor_sunflower.db")
    SQLITE_I18N_EN_PATH = os.path.join(INSTANCE_DIR, "i18n_en.db")
    SQLITE_I18N_KM_PATH = os.path.join(INSTANCE_DIR, "i18n_km.db")
    _default_sqlite_uri = f"sqlite:///{SQLITE_DB_PATH}"
    _default_i18n_en_sqlite_uri = f"sqlite:///{SQLITE_I18N_EN_PATH}"
    _default_i18n_km_sqlite_uri = f"sqlite:///{SQLITE_I18N_KM_PATH}"

    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_DB = os.environ.get("MYSQL_DB", "doctor_sunflower")

    _auth = quote_plus(MYSQL_USER)
    if MYSQL_PASSWORD:
        _auth = f"{_auth}:{quote_plus(MYSQL_PASSWORD)}"

    _default_mysql_uri = (
        f"mysql+pymysql://{_auth}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )

    I18N_EN_DB = os.environ.get("I18N_EN_DB", f"{MYSQL_DB}_en")
    I18N_KM_DB = os.environ.get("I18N_KM_DB", f"{MYSQL_DB}_km")

    _default_i18n_en_mysql_uri = (
        f"mysql+pymysql://{_auth}@{MYSQL_HOST}:{MYSQL_PORT}/{I18N_EN_DB}?charset=utf8mb4"
    )
    _default_i18n_km_mysql_uri = (
        f"mysql+pymysql://{_auth}@{MYSQL_HOST}:{MYSQL_PORT}/{I18N_KM_DB}?charset=utf8mb4"
    )

    _database_url = os.environ.get("DATABASE_URL", _default_sqlite_uri)

    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        _database_url,
        env_name="DATABASE_URL",
    )

    _main_is_mysql = SQLALCHEMY_DATABASE_URI.startswith("mysql+pymysql://")

    _i18n_en_database_url = os.environ.get("I18N_EN_DATABASE_URL")
    if _i18n_en_database_url:
        I18N_EN_DATABASE_URL = _normalize_database_url(
            _i18n_en_database_url,
            env_name="I18N_EN_DATABASE_URL",
        )
    elif _main_is_mysql:
        I18N_EN_DATABASE_URL = _default_i18n_en_mysql_uri
    else:
        I18N_EN_DATABASE_URL = _default_i18n_en_sqlite_uri

    _i18n_km_database_url = os.environ.get("I18N_KM_DATABASE_URL")
    if _i18n_km_database_url:
        I18N_KM_DATABASE_URL = _normalize_database_url(
            _i18n_km_database_url,
            env_name="I18N_KM_DATABASE_URL",
        )
    elif _main_is_mysql:
        I18N_KM_DATABASE_URL = _default_i18n_km_mysql_uri
    else:
        I18N_KM_DATABASE_URL = _default_i18n_km_sqlite_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
        "i18n_en": I18N_EN_DATABASE_URL,
        "i18n_km": I18N_KM_DATABASE_URL,
    }

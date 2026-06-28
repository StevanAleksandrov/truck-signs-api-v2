"""
Django settings for tsa_app project.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Configure Django logging
logger = logging.getLogger(__name__)

# Configure logging format
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(funcName)s:%(lineno)d",  # noqa E501
    datefmt="%Y-%m-%d_%H-%M-%S",
)
logger.setLevel(level="INFO")

# path: truck-signs-api/src = root of project tsa_app
BASE_DIR = Path(__file__).resolve().parent.parent
# path: truck-signs-api = root of project truck-signs-api
ROOT_BASE_DIR = BASE_DIR.parent
TEMPLATES_DIR = BASE_DIR / "templates"

# Load environment variables from a local .env file if present.
# In Docker Compose, variables are injected through env_file and do not require
# a physical .env file inside the container.
env_file = ROOT_BASE_DIR / ".env"

if env_file.exists():
    load_dotenv(env_file)
    logger.info("loaded environment variables from .env file")

else:
    logger.info("no local .env file found, using existing environment variables")
# read configuration from environment, set secure defaults where possible
# adjust django settings depending on environment configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")

MODE = os.getenv("MODE")
DEBUG = os.getenv("DEBUG_ENABLED", "False") == "True"

if DEBUG is True and MODE != "":
    logger.info("could not detect MODE variable, setting to 'dev'")
    MODE = "dev"

elif not MODE or MODE == "":
    logger.info("could not detect MODE variable, setting to 'prod'")
    MODE = "prod"

if MODE == "prod":
    logger.info("running in production mode, ensure 'DEBUG' is disabled")
    DEBUG = False
    logger.setLevel(level=LOG_LEVEL)

else:
    # dev mode
    logger.info("running in development mode, enabling 'DEBUG'")
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    logger.setLevel(level=LOG_LEVEL)

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-production")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "cloudinary",
    "tsa_products",
    "django.contrib.admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tsa_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tsa_app.wsgi.application"

db_engine = "django.db.backends.sqlite3" if MODE != "prod" else "django.db.backends.postgresql"  # noqa E501

pg_config = {
    "ENGINE": db_engine,
    "NAME": os.getenv("DB_NAME", "trucksigns_db"),
    "USER": os.getenv("DB_USER"),
    "PASSWORD": os.getenv("DB_PASSWORD"),
    "HOST": os.getenv("DB_HOST", "localhost"),
    "PORT": os.getenv("DB_PORT", "5432"),
}

sqlite_config = {
    "ENGINE": db_engine,
    "NAME": BASE_DIR / "db.sqlite3",
}

db_config = sqlite_config if MODE != "prod" else pg_config

DATABASES = {"default": db_config}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles/")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles/")

CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000",
).split(",")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUD_NAME", ""),
    "API_KEY": os.getenv("CLOUD_API_KEY", ""),
    "API_SECRET": os.getenv("CLOUD_API_SECRET", ""),
}

# Only use Cloudinary in production if configured
if os.getenv("CLOUD_NAME", ""):
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Debugging output of settings
if MODE != "prod" or DEBUG is True:
    logger.debug("dumping settings for debugging/development purposes:")
    print("")
    print(f"[{"---" * 20} \t\tSTART SETTINGS DEBUG INFO \t{"---" * 20}]")
    print("")
    print(f"[ROOT BASE DIR]: \t\t{ROOT_BASE_DIR}")
    print(f"[BASE DIR]: \t\t\t{BASE_DIR}")
    print(f"[TEMPLATE DIR]: \t\t{TEMPLATES_DIR}")
    print(f"[MODE]: \t\t\t{MODE}")
    print(f"[DEBUG MODE ENABLED]: \t\t{DEBUG}")
    print(f"[ALLOWED HOSTS]: \t\t{ALLOWED_HOSTS}")
    print("[DB CONFIG]:")
    for key, value in DATABASES["default"].items():
        print(f"  {key}: \t\t\t{value}")
    print("")
    print(f"[{"---" * 20} \t\tEND SETTINGS DEBUG INFO \t{"---" * 20}]")
    print("")

from .settings import *

SECRET_KEY = "chave-ficticia-exclusiva-para-testes"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "optio@example.test"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": "cliente-ficticio",
            "secret": "segredo-ficticio",
            "key": "",
        },
        "SCOPE": ["profile", "email"],
    }
}

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
from scan_api.settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Desabilita aviso de DEBUG+produção no ambiente de testes
import warnings  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)

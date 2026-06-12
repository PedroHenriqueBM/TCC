import os
import secrets
from pathlib import Path
from flask import Flask


def _load_app_settings() -> None:
    """Load persisted settings into env before anything else uses them."""
    try:
        from AppSettings import load_all_into_env
        load_all_into_env()
    except Exception:
        pass


def _stable_secret_key() -> str:
    """Retorna a secret_key do env, ou gera/reutiliza uma salva em arquivo."""
    if key := os.environ.get("FLASK_SECRET_KEY"):
        return key
    key_file = Path(__file__).parent.parent.parent / ".flask_secret_key"
    if key_file.exists():
        return key_file.read_text().strip()
    key = secrets.token_hex(32)
    key_file.write_text(key)
    return key


def create_app() -> Flask:
    _load_app_settings()

    app = Flask(__name__, template_folder="templates")
    app.secret_key = _stable_secret_key()

    from .routes import register_routes
    register_routes(app)

    return app

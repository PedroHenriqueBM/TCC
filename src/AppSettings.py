"""
Gerenciamento de configurações persistentes da aplicação.
As configurações ficam em .app_settings (JSON) na raiz do projeto.
Variáveis de ambiente sempre têm prioridade.
"""
import json
import os
from pathlib import Path

_SETTINGS_FILE = Path(__file__).parent.parent / ".app_settings"


def _load() -> dict:
    if _SETTINGS_FILE.exists():
        try:
            return json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    _SETTINGS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_setting(key: str, default: str = "") -> str:
    """Returns env var if set, otherwise reads from .app_settings file."""
    env_val = os.environ.get(key.upper(), "").strip()
    if env_val:
        return env_val
    return _load().get(key, default)


def set_setting(key: str, value: str) -> None:
    """Persists value in .app_settings and updates the running process env."""
    data = _load()
    data[key] = value
    _save(data)
    if value:
        os.environ[key.upper()] = value
    else:
        os.environ.pop(key.upper(), None)


def load_all_into_env() -> None:
    """Called at startup: loads .app_settings values into os.environ for any key not already set."""
    for key, value in _load().items():
        env_key = key.upper()
        if value and not os.environ.get(env_key):
            os.environ[env_key] = value

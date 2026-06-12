import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from web import create_app

app = create_app()

if __name__ == "__main__":
    # use_reloader=False evita que o Werkzeug reinicie o servidor ao detectar
    # novos arquivos .py gerados pelo Playwright em src/Storage/
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)

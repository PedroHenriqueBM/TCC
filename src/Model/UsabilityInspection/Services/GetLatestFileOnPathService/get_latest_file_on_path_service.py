from pathlib import Path

def get_latest_file_on_path_service(folder: str):
    folder_path = Path(folder)

    files = [f for f in folder_path.iterdir() if f.is_file()]

    if not files:
        raise FileNotFoundError("Nenhum arquivo encontrado na pasta.")

    last_file = max(files, key=lambda f: f.stat().st_mtime)
    return str(last_file)
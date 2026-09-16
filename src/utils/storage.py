import os
from datetime import date


def get_today_output_dir() -> str:
    path = os.path.join("output", date.today().isoformat())
    os.makedirs(path, exist_ok=True)
    return path


def save_text(dir_path: str, filename: str, content: str) -> str:
    full_path = os.path.join(dir_path, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return full_path

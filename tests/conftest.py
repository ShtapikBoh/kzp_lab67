"""Спільні допоміжні функції тестів."""

from pathlib import Path

HEADER = "subject,teacher,day,period,room\n"


def write_csv(path: Path, text: str) -> Path:
    """Записує CSV-файл у UTF-8 без перетворення роздільників."""
    with path.open("w", encoding="utf-8", newline="") as target:
        target.write(text)
    return path

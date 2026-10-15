"""Формування й запис текстового звіту."""

from pathlib import Path


def format_report(summary: dict[str, object]) -> str:
    """Форматує підсумок у детермінований текстовий звіт."""
    lines = [
        f"Записів у файлі: {summary['total']}",
        f"День: {summary['day']}",
        f"Занять у цей день: {summary['lessons']}",
        "Заняття за викладачами:",
    ]
    teachers = summary["teachers"]
    if teachers:
        lines.extend(f"  {name}: {count}" for name, count in sorted(teachers.items()))
    else:
        lines.append("  немає даних")
    rooms = summary["rooms"]
    lines.append(
        "Аудиторії: " + (", ".join(str(room) for room in rooms) or "немає даних")
    )
    bounds = summary["bounds"]
    if bounds is None:
        lines.append("Перша пара: немає даних")
        lines.append("Остання пара: немає даних")
    else:
        lines.append(f"Перша пара: {bounds[0]}")
        lines.append(f"Остання пара: {bounds[1]}")
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Записує звіт у UTF-8; каталог створюється, якщо його немає."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # with гарантує закриття файла навіть у разі помилки запису.
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)

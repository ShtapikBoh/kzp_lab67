"""Формування й запис текстового звіту."""

from pathlib import Path

from kzp_lab07.models import ScheduleSummary


def format_report(summary: ScheduleSummary) -> str:
    """Форматує підсумок у детермінований текстовий звіт.

    Перші рядки збігаються зі звітом лабораторної № 6; у кінці додано блок
    «Завантаження аудиторій».
    """
    lines = [
        f"Записів у файлі: {summary.total}",
        f"День: {summary.day}",
        f"Занять у цей день: {summary.lessons}",
        "Заняття за викладачами:",
    ]
    if summary.teachers:
        lines.extend(f"  {name}: {count}" for name, count in summary.teachers)
    else:
        lines.append("  немає даних")
    room_text = ", ".join(str(room) for room in summary.rooms) or "немає даних"
    lines.append(f"Аудиторії: {room_text}")
    if summary.bounds is None:
        lines.append("Перша пара: немає даних")
        lines.append("Остання пара: немає даних")
    else:
        lines.append(f"Перша пара: {summary.bounds[0]}")
        lines.append(f"Остання пара: {summary.bounds[1]}")
    lines.append("Завантаження аудиторій:")
    if summary.room_loads:
        lines.extend(
            f"  {load.room}: {load.lessons} зан., {load.need} год"
            for load in summary.room_loads
        )
    else:
        lines.append("  немає даних")
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Записує звіт у UTF-8; каталог створюється, якщо його немає."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # with гарантує закриття файла навіть у разі помилки запису.
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)

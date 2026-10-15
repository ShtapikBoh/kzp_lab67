"""Читання CSV і перетворення рядків на об'єкти розкладу."""

import csv
from pathlib import Path

from kzp_lab07.errors import DataError
from kzp_lab07.models import LECTURE_MIN_ROOM, Lecture, Lesson, Practice

TEXT_FIELDS = ("subject", "teacher", "day")
NUMBER_FIELDS = ("period", "room")
REQUIRED_FIELDS = TEXT_FIELDS + NUMBER_FIELDS


def parse_number(value: str, row_number: int, field: str) -> int:
    """Перетворює поле на додатне ціле й додає номер рядка до помилки."""
    try:
        number = int(value)
    except ValueError as error:
        raise DataError(
            f"Рядок {row_number}: поле {field} має бути цілим числом"
        ) from error
    if number <= 0:
        raise DataError(f"Рядок {row_number}: поле {field} має бути більшим за 0")
    return number


def lesson_class_for(room: int) -> type[Lesson]:
    """Обирає підтип за аудиторією: від ``LECTURE_MIN_ROOM`` — лекція."""
    return Lecture if room >= LECTURE_MIN_ROOM else Practice


def build_lesson(row: dict, row_number: int) -> Lesson:
    """Перетворює один рядок CSV на заняття відповідного підтипу."""
    if None in row:
        raise DataError(f"Рядок {row_number}: забагато значень у рядку")
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or not value.strip():
            raise DataError(f"Рядок {row_number}: поле {field} відсутнє або порожнє")
    period = parse_number(row["period"].strip(), row_number, "period")
    room = parse_number(row["room"].strip(), row_number, "room")
    cls = lesson_class_for(room)
    try:
        return cls(row["subject"], row["teacher"], row["day"], period, room)
    except ValueError as error:
        raise DataError(f"Рядок {row_number}: {error}") from error


def load_lessons(path: Path) -> list[Lesson]:
    """Читає CSV (UTF-8) і повертає заняття.

    Файл із заголовком і без записів дає порожній список. Повністю порожній файл,
    відсутній стовпець, хибне або порожнє значення — це ``DataError`` з номером
    рядка (заголовок має номер 1) або назвою стовпця. Вхідний файл не змінюється.
    """
    try:
        with path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            header = reader.fieldnames
            if header is None:
                raise DataError("Файл порожній: немає рядка заголовка")
            missing = [field for field in REQUIRED_FIELDS if field not in header]
            if missing:
                raise DataError("Відсутні стовпці: " + ", ".join(missing))
            return [build_lesson(row, number) for number, row in enumerate(reader, 2)]
    except UnicodeDecodeError as error:
        raise DataError(f"Файл {path} не є коректним UTF-8") from error

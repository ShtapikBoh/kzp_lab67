"""Читання CSV і перетворення рядків на типізовані записи."""

import csv
from pathlib import Path
from typing import TypedDict

from kzp_lab06.errors import DataError

TEXT_FIELDS = ("subject", "teacher", "day")
NUMBER_FIELDS = ("period", "room")
REQUIRED_FIELDS = TEXT_FIELDS + NUMBER_FIELDS


class LessonRecord(TypedDict):
    """Одне заняття розкладу з типізованими полями."""

    subject: str
    teacher: str
    day: str
    period: int
    room: int


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


def parse_row(row: dict, row_number: int) -> LessonRecord:
    """Перевіряє один рядок CSV і повертає типізований запис."""
    if None in row:
        raise DataError(f"Рядок {row_number}: забагато значень у рядку")
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or not value.strip():
            raise DataError(f"Рядок {row_number}: поле {field} відсутнє або порожнє")
    return {
        "subject": row["subject"].strip(),
        "teacher": row["teacher"].strip(),
        "day": row["day"].strip(),
        "period": parse_number(row["period"].strip(), row_number, "period"),
        "room": parse_number(row["room"].strip(), row_number, "room"),
    }


def load_records(path: Path) -> list[LessonRecord]:
    """Читає CSV (UTF-8) і повертає записи.

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
            return [parse_row(row, number) for number, row in enumerate(reader, 2)]
    except UnicodeDecodeError as error:
        raise DataError(f"Файл {path} не є коректним UTF-8") from error

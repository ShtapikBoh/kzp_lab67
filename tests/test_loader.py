"""Тести завантаження й перетворення CSV."""

from pathlib import Path

import pytest

from conftest import HEADER, write_csv
from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records, parse_number


def test_loads_typed_records(tmp_path: Path) -> None:
    """Текст перетворюється на рядки й цілі числа."""
    path = write_csv(
        tmp_path / "in.csv", HEADER + "Фізика,Бойко А. А.,Вівторок,2,120\n"
    )

    assert load_records(path) == [
        {
            "subject": "Фізика",
            "teacher": "Бойко А. А.",
            "day": "Вівторок",
            "period": 2,
            "room": 120,
        }
    ]


def test_header_only_gives_empty_list(tmp_path: Path) -> None:
    """Файл лише із заголовком — коректний порожній набір."""
    assert load_records(write_csv(tmp_path / "in.csv", HEADER)) == []


def test_completely_empty_file_is_error(tmp_path: Path) -> None:
    """Файл без заголовка не можна обробити."""
    with pytest.raises(DataError, match="порожній"):
        load_records(write_csv(tmp_path / "in.csv", ""))


def test_missing_column_names_the_column(tmp_path: Path) -> None:
    """Відсутній стовпець називається в повідомленні."""
    path = write_csv(tmp_path / "in.csv", "subject,teacher,day,period\nА,Б,В,1\n")

    with pytest.raises(DataError, match="room"):
        load_records(path)


def test_missing_value_in_short_row(tmp_path: Path) -> None:
    """Короткий рядок: відсутнє значення з номером рядка й полем."""
    path = write_csv(tmp_path / "in.csv", HEADER + "А,Б,В,1,10\nГ,Д,Е\n")

    with pytest.raises(DataError, match=r"Рядок 3: поле period"):
        load_records(path)


def test_empty_text_value_is_error(tmp_path: Path) -> None:
    """Порожнє текстове поле — помилка з назвою поля."""
    path = write_csv(tmp_path / "in.csv", HEADER + " ,Б,В,1,10\n")

    with pytest.raises(DataError, match=r"Рядок 2: поле subject"):
        load_records(path)


def test_extra_values_are_error(tmp_path: Path) -> None:
    """Зайві значення в рядку не ігноруються мовчки."""
    path = write_csv(tmp_path / "in.csv", HEADER + "А,Б,В,1,10,зайве\n")

    with pytest.raises(DataError, match="забагато"):
        load_records(path)


def test_bad_number_keeps_cause(tmp_path: Path) -> None:
    """Хибне число: номер рядка, назва поля й першопричина."""
    path = write_csv(tmp_path / "in.csv", HEADER + "А,Б,В,abc,10\n")

    with pytest.raises(DataError, match=r"Рядок 2: поле period") as info:
        load_records(path)

    assert isinstance(info.value.__cause__, ValueError)


@pytest.mark.parametrize("value", ["0", "-5"])
def test_non_positive_number_is_error(tmp_path: Path, value: str) -> None:
    """Нуль і від'ємне число відхиляються."""
    path = write_csv(tmp_path / "in.csv", HEADER + f"А,Б,В,1,{value}\n")

    with pytest.raises(DataError, match=r"поле room"):
        load_records(path)


def test_parse_number_accepts_boundary_one() -> None:
    """Найменше допустиме значення — 1."""
    assert parse_number("1", 2, "period") == 1


def test_comma_quote_and_newline_in_text(tmp_path: Path) -> None:
    """Кома, лапки й переніс рядка в полі не ламають розбір."""
    text = (
        HEADER
        + '"Мережі, протоколи",Т,В,1,10\n'
        + '"Математика ""вища""",Т,В,2,10\n'
        + '"Фізика\n(лабораторна)",Т,В,3,10\n'
    )

    subjects = [
        r["subject"] for r in load_records(write_csv(tmp_path / "in.csv", text))
    ]

    assert subjects == [
        "Мережі, протоколи",
        'Математика "вища"',
        "Фізика\n(лабораторна)",
    ]


def test_duplicates_are_kept(tmp_path: Path) -> None:
    """Однакові рядки не відкидаються завантажувачем."""
    path = write_csv(tmp_path / "in.csv", HEADER + "А,Б,В,1,10\nА,Б,В,1,10\n")

    assert len(load_records(path)) == 2


def test_invalid_utf8_is_data_error(tmp_path: Path) -> None:
    """Файл не в UTF-8 дає DataError із першопричиною."""
    path = tmp_path / "in.csv"
    path.write_bytes(b"subject,teacher,day,period,room\n\xff\xfe,B,C,1,10\n")

    with pytest.raises(DataError, match="UTF-8") as info:
        load_records(path)

    assert isinstance(info.value.__cause__, UnicodeDecodeError)


def test_input_file_is_not_modified(tmp_path: Path) -> None:
    """Читання не змінює вхідний файл."""
    path = write_csv(tmp_path / "in.csv", HEADER + "А,Б,В,1,10\n")
    before = path.read_bytes()

    load_records(path)

    assert path.read_bytes() == before


def test_missing_file_raises_os_error(tmp_path: Path) -> None:
    """Відсутній файл — OSError (його обробляє межа CLI)."""
    with pytest.raises(OSError):
        load_records(tmp_path / "немає.csv")

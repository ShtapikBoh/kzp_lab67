"""Еквівалентність звітів лабораторних № 6 (словники) і № 7 (об'єкти)."""

from pathlib import Path

import pytest

from conftest import HEADER, write_csv
from kzp_lab06.analysis import make_summary as make_summary06
from kzp_lab06.loader import load_records
from kzp_lab06.reporting import format_report as format_report06
from kzp_lab07.analysis import make_summary as make_summary07
from kzp_lab07.loader import load_lessons
from kzp_lab07.reporting import format_report as format_report07

CSV_TEXT = (
    HEADER
    + "Програмування,Олексів М. В.,Понеділок,1,101\n"
    + "Кросплатформні засоби,Рудик Ю. І.,Вівторок,1,215\n"
    + "Бази даних,Коваленко О. П.,Середа,2,98\n"
    + "Алгоритми,Олексів М. В.,Понеділок,3,101\n"
    + '"Мережі, протоколи",Сидоренко Н. Г.,Понеділок,2,305\n'
)


def reports(path: Path, day: str) -> tuple[str, str]:
    """Повертає звіти старої й нової реалізацій для одного CSV."""
    old = format_report06(make_summary06(load_records(path), day))
    new = format_report07(make_summary07(load_lessons(path), day))
    return old, new


@pytest.mark.parametrize("day", ["Понеділок", "Вівторок", "Середа", "Четвер"])
def test_new_report_starts_with_old_report(tmp_path: Path, day: str) -> None:
    """Звіт лаби 7 починається з незмінного звіту лаби 6."""
    path = write_csv(tmp_path / "in.csv", CSV_TEXT)

    old, new = reports(path, day)

    assert new.startswith(old)


def test_new_report_only_adds_room_load_block(tmp_path: Path) -> None:
    """Єдина відмінність — додатковий блок завантаження аудиторій."""
    path = write_csv(tmp_path / "in.csv", CSV_TEXT)

    old, new = reports(path, "Понеділок")

    assert new[len(old) :].startswith("Завантаження аудиторій:\n")


def test_empty_input_is_compatible(tmp_path: Path) -> None:
    """Порожній набір також дає сумісний звіт."""
    path = write_csv(tmp_path / "in.csv", HEADER)

    old, new = reports(path, "Понеділок")

    assert new.startswith(old)


@pytest.mark.parametrize(
    "row",
    ["А,Б,В,abc,10", "А,Б,В,1,0", "А,Б,В,1", " ,Б,В,1,10", "А,Б,В,1,10,зайве"],
)
def test_error_messages_match_old_loader(tmp_path: Path, row: str) -> None:
    """Повідомлення про хибні дані збігаються зі старим завантажувачем."""
    path = write_csv(tmp_path / "in.csv", HEADER + row + "\n")

    with pytest.raises(ValueError) as old:
        load_records(path)
    with pytest.raises(ValueError) as new:
        load_lessons(path)

    assert str(new.value) == str(old.value)


def test_object_and_dict_models_give_same_counts(tmp_path: Path) -> None:
    """Кількість записів і викладачів збігаються в обох моделях."""
    path = write_csv(tmp_path / "in.csv", CSV_TEXT)

    assert len(load_records(path)) == len(load_lessons(path))

"""Тести функцій аналізу."""

import pytest

from kzp_lab06.analysis import (
    count_by_teacher,
    filter_by_day,
    make_summary,
    period_bounds,
    summarize,
    unique_rooms,
)
from kzp_lab06.loader import LessonRecord


def lesson(
    subject: str = "А",
    teacher: str = "Т1",
    day: str = "Понеділок",
    period: int = 1,
    room: int = 10,
) -> LessonRecord:
    """Створює запис для тестів."""
    return {
        "subject": subject,
        "teacher": teacher,
        "day": day,
        "period": period,
        "room": room,
    }


def test_filter_by_day_ignores_case_and_spaces() -> None:
    """Відбір не залежить від регістру й пробілів."""
    records = [lesson(day="Понеділок"), lesson(day="Вівторок")]

    assert filter_by_day(records, " понеділок ") == [records[0]]


def test_filter_by_day_without_matches_is_empty() -> None:
    """Якщо занять немає, результат порожній."""
    assert filter_by_day([lesson(day="Вівторок")], "Середа") == []


def test_count_by_teacher_counts_duplicates_and_sorts_keys() -> None:
    """Дублікати рахуються, ключі відсортовано."""
    records = [lesson(teacher="Я"), lesson(teacher="А"), lesson(teacher="Я")]

    result = count_by_teacher(records)

    assert result == {"А": 1, "Я": 2}
    assert list(result) == ["А", "Я"]


def test_count_by_teacher_of_empty_list() -> None:
    """Порожній вхід дає порожній словник."""
    assert count_by_teacher([]) == {}


def test_unique_rooms_removes_duplicates() -> None:
    """Множина аудиторій не має повторів."""
    records = [lesson(room=101), lesson(room=101), lesson(room=98)]

    assert unique_rooms(records) == {98, 101}


def test_period_bounds() -> None:
    """Перша й остання пара."""
    records = [lesson(period=2), lesson(period=1), lesson(period=3)]

    assert period_bounds(records) == (1, 3)


def test_period_bounds_single_record() -> None:
    """Для одного запису перша й остання пара збігаються."""
    assert period_bounds([lesson(period=2)]) == (2, 2)


def test_period_bounds_of_empty_list_is_none() -> None:
    """Для порожнього набору межі невідомі."""
    assert period_bounds([]) is None


def test_summarize_defaults_count_only() -> None:
    """Без метрик повертається лише кількість."""
    assert summarize([lesson(), lesson()]) == {"count": 2.0}


def test_summarize_args_and_kwargs() -> None:
    """*args задають метрики, **kwargs — підписи, minimum_period — відбір."""
    records = [lesson(period=1, room=10), lesson(period=2, room=20)]

    result = summarize(records, "period", "room", minimum_period=2, period="Пари")

    assert result == {"count": 1.0, "Пари": 2.0, "room": 20.0}


def test_summarize_unknown_metric_is_error() -> None:
    """Невідома метрика відхиляється явно."""
    with pytest.raises(ValueError, match="Невідома метрика"):
        summarize([lesson()], "subject")


def test_summarize_zero_when_everything_filtered() -> None:
    """Якщо всі записи відсіяно, метрики дорівнюють 0.0."""
    result = summarize([lesson(period=1)], "room", minimum_period=5)

    assert result == {"count": 0.0, "room": 0.0}


def test_summarize_does_not_change_input() -> None:
    """Вхідний список не змінюється."""
    records = [lesson(), lesson(period=2)]
    before = [dict(record) for record in records]

    summarize(records, "period")

    assert records == before


def test_make_summary_for_day() -> None:
    """Підсумок за днем: заняття, викладачі, аудиторії, межі пар."""
    records = [
        lesson(teacher="Т1", period=1, room=101),
        lesson(teacher="Т1", period=3, room=101),
        lesson(teacher="Т2", period=2, room=110),
        lesson(teacher="Т3", day="Вівторок", period=1, room=5),
    ]

    summary = make_summary(records, "Понеділок")

    assert summary == {
        "total": 4,
        "day": "Понеділок",
        "lessons": 3,
        "teachers": {"Т1": 2, "Т2": 1},
        "rooms": [101, 110],
        "bounds": (1, 3),
    }


def test_make_summary_of_empty_input() -> None:
    """Порожній вхід дає нульовий підсумок."""
    summary = make_summary([], "Понеділок")

    assert summary["lessons"] == 0
    assert summary["teachers"] == {}
    assert summary["rooms"] == []
    assert summary["bounds"] is None

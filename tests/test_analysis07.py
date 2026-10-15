"""Тести аналізу об'єктів (пакет kzp_lab07)."""

import dataclasses

from kzp_lab07.analysis import (
    count_by_teacher,
    filter_by_day,
    make_summary,
    period_bounds,
    room_loads,
    unique_rooms,
)
from kzp_lab07.models import Lecture, Lesson, Practice, RoomLoad, ScheduleSummary


def lesson(
    cls: type[Lesson] = Practice,
    teacher: str = "Т1",
    day: str = "Понеділок",
    period: int = 1,
    room: int = 10,
) -> Lesson:
    """Створює заняття для тестів."""
    return cls("Предмет", teacher, day, period, room)


def test_filter_by_day_ignores_case_and_spaces() -> None:
    """Відбір не залежить від регістру й пробілів."""
    lessons = [lesson(day="Понеділок"), lesson(day="Вівторок")]

    assert filter_by_day(lessons, " понеділок ") == [lessons[0]]


def test_filter_by_day_without_matches_is_empty() -> None:
    """Якщо занять немає, результат порожній."""
    assert filter_by_day([lesson(day="Вівторок")], "Середа") == []


def test_count_by_teacher_counts_duplicates_and_sorts_keys() -> None:
    """Дублікати рахуються, ключі відсортовано."""
    lessons = [lesson(teacher="Я"), lesson(teacher="А"), lesson(teacher="Я")]

    result = count_by_teacher(lessons)

    assert result == {"А": 1, "Я": 2}
    assert list(result) == ["А", "Я"]


def test_count_by_teacher_of_empty_list() -> None:
    """Порожній вхід дає порожній словник."""
    assert count_by_teacher([]) == {}


def test_unique_rooms_removes_duplicates() -> None:
    """Множина аудиторій не має повторів."""
    lessons = [lesson(room=101), lesson(room=101), lesson(room=98)]

    assert unique_rooms(lessons) == {98, 101}


def test_period_bounds_cases() -> None:
    """Межі пар: кілька записів, один запис, порожній вхід."""
    assert period_bounds([lesson(period=2), lesson(period=1), lesson(period=3)]) == (
        1,
        3,
    )
    assert period_bounds([lesson(period=2)]) == (2, 2)
    assert period_bounds([]) is None


def test_room_loads_sums_polymorphic_need_per_room() -> None:
    """Потреба підсумовується поліморфно: лекція 2, практика 1."""
    lessons = [
        lesson(Lecture, room=215),
        lesson(Practice, room=215),
        lesson(Practice, room=98),
    ]

    assert room_loads(lessons) == (RoomLoad(98, 1, 1), RoomLoad(215, 2, 3))


def test_room_loads_of_empty_list() -> None:
    """Порожній вхід дає порожній кортеж."""
    assert room_loads([]) == ()


def test_make_summary_for_day() -> None:
    """Підсумок за днем: заняття, викладачі, аудиторії, межі, завантаження."""
    lessons = [
        lesson(Practice, "Т1", period=1, room=101),
        lesson(Practice, "Т1", period=3, room=101),
        lesson(Lecture, "Т2", period=2, room=215),
        lesson(Practice, "Т3", day="Вівторок", period=1, room=5),
    ]

    summary = make_summary(lessons, "Понеділок")

    assert summary == ScheduleSummary(
        total=4,
        day="Понеділок",
        lessons=3,
        teachers=(("Т1", 2), ("Т2", 1)),
        rooms=(101, 215),
        bounds=(1, 3),
        room_loads=(RoomLoad(101, 2, 2), RoomLoad(215, 1, 2)),
    )


def test_make_summary_of_empty_input() -> None:
    """Порожній вхід дає нульовий підсумок."""
    summary = make_summary([], "Понеділок")

    assert summary.lessons == 0
    assert summary.teachers == ()
    assert summary.rooms == ()
    assert summary.bounds is None
    assert summary.room_loads == ()


def test_make_summary_is_frozen_dataclass() -> None:
    """Підсумок — незмінний dataclass."""
    summary = make_summary([lesson()], "Понеділок")

    assert dataclasses.is_dataclass(summary)
    assert summary.__dataclass_params__.frozen  # type: ignore[attr-defined]


def test_analysis_does_not_change_input() -> None:
    """Вхідний список не змінюється."""
    lessons = [lesson(period=2), lesson(period=1)]
    before = list(lessons)

    make_summary(lessons, "Понеділок")

    assert lessons == before

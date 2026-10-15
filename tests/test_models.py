"""Тести моделей: властивості, спеціальні методи, підтипи, dataclass, протокол."""

import dataclasses

import pytest

from kzp_lab07.analysis import room_loads
from kzp_lab07.models import Lecture, Lesson, Practice, RoomLoad, ScheduleSummary


def make_lesson(cls: type[Lesson] = Practice, **changes: object) -> Lesson:
    """Створює заняття для тестів із можливістю змінити поля."""
    fields: dict[str, object] = {
        "subject": "Фізика",
        "teacher": "Бойко А. А.",
        "day": "Вівторок",
        "period": 2,
        "room": 120,
    }
    fields.update(changes)
    return cls(**fields)


def test_properties_return_values_and_trim_text() -> None:
    """Властивості повертають значення, текст обрізається."""
    lesson = make_lesson(subject=" Фізика ", teacher=" Бойко А. А. ", day=" Вівторок ")

    assert (lesson.subject, lesson.teacher, lesson.day) == (
        "Фізика",
        "Бойко А. А.",
        "Вівторок",
    )
    assert (lesson.period, lesson.room) == (2, 120)


@pytest.mark.parametrize("field", ["subject", "teacher", "day"])
@pytest.mark.parametrize("value", ["", "   "])
def test_constructor_rejects_blank_text(field: str, value: str) -> None:
    """Порожній або пробільний текст відхиляється."""
    with pytest.raises(ValueError, match=field):
        make_lesson(**{field: value})


@pytest.mark.parametrize("field", ["period", "room"])
@pytest.mark.parametrize("value", [0, -1, -100])
def test_constructor_rejects_non_positive_numbers(field: str, value: int) -> None:
    """Нуль і від'ємні числа відхиляються."""
    with pytest.raises(ValueError, match=field):
        make_lesson(**{field: value})


@pytest.mark.parametrize("field", ["period", "room"])
@pytest.mark.parametrize("value", ["5", 2.5, None, True])
def test_constructor_rejects_non_integers(field: str, value: object) -> None:
    """Не цілі значення (включно з bool) відхиляються."""
    with pytest.raises(ValueError, match="цілим"):
        make_lesson(**{field: value})


def test_setter_accepts_valid_and_boundary_value() -> None:
    """Setter приймає коректне та граничне значення 1."""
    lesson = make_lesson()

    lesson.period = 5
    lesson.room = 1

    assert (lesson.period, lesson.room) == (5, 1)


def test_setter_rejects_invalid_value_and_keeps_old_one() -> None:
    """Помилковий setter не змінює попереднє значення."""
    lesson = make_lesson()

    with pytest.raises(ValueError, match="period"):
        lesson.period = 0
    with pytest.raises(ValueError, match="subject"):
        lesson.subject = " "

    assert lesson.period == 2
    assert lesson.subject == "Фізика"


def test_str_is_readable() -> None:
    """__str__ — коротке подання для читача."""
    assert str(make_lesson()) == "Фізика (Бойко А. А., Вівторок, пара 2, ауд. 120)"


def test_repr_is_diagnostic_and_names_subtype() -> None:
    """__repr__ містить назву підтипу й усі поля."""
    assert repr(make_lesson(Lecture)) == (
        "Lecture(subject='Фізика', teacher='Бойко А. А.', day='Вівторок', "
        "period=2, room=120)"
    )


def test_equal_lessons_of_same_type() -> None:
    """Однакові за типом і полями заняття рівні."""
    assert make_lesson() == make_lesson()


def test_changed_field_breaks_equality() -> None:
    """Зміна будь-якого поля робить заняття нерівними."""
    base = make_lesson()

    assert base != make_lesson(subject="Хімія")
    assert base != make_lesson(teacher="Інший")
    assert base != make_lesson(day="Середа")
    assert base != make_lesson(period=3)
    assert base != make_lesson(room=121)


def test_different_subtypes_with_same_fields_are_not_equal() -> None:
    """Лекція й практика з однаковими полями — різні об'єкти."""
    assert make_lesson(Lecture) != make_lesson(Practice)


def test_eq_returns_not_implemented_for_foreign_type() -> None:
    """__eq__ повертає NotImplemented для несумісного типу."""
    lesson = make_lesson()

    assert lesson.__eq__("Фізика") is NotImplemented
    assert lesson != "Фізика"
    assert lesson != 120


def test_lesson_is_unhashable_because_it_is_mutable() -> None:
    """Змінюваний об'єкт не може бути ключем словника."""
    with pytest.raises(TypeError):
        hash(make_lesson())


def test_ordering_uses_period_room_subject() -> None:
    """Впорядкування: пара, потім аудиторія, потім предмет."""
    late = make_lesson(period=3, room=1, subject="А")
    early_big_room = make_lesson(period=1, room=200, subject="Б")
    early_small_room = make_lesson(period=1, room=5, subject="В")

    assert sorted([late, early_big_room, early_small_room]) == [
        early_small_room,
        early_big_room,
        late,
    ]
    assert early_small_room < late


def test_ordering_with_foreign_type_is_not_supported() -> None:
    """Порівняння з чужим типом через < дає TypeError."""
    with pytest.raises(TypeError):
        make_lesson() < "x"  # noqa: B015


def test_sort_key_can_be_used_with_sorted() -> None:
    """key працює для sorted без додаткових методів."""
    lessons = [make_lesson(period=2), make_lesson(period=1)]

    assert [lesson.period for lesson in sorted(lessons, key=lambda x: x.sort_key)] == [
        1,
        2,
    ]


def test_base_lesson_does_not_define_room_need() -> None:
    """Базова операція лише оголошена."""
    with pytest.raises(NotImplementedError):
        make_lesson(Lesson).room_need()


def test_subtypes_have_different_room_need() -> None:
    """Підтипи по-різному реалізують спільну операцію."""
    assert make_lesson(Lecture).room_need() == 2
    assert make_lesson(Practice).room_need() == 1
    assert make_lesson(Lecture).room_need() != make_lesson(Practice).room_need()


def test_subtypes_are_lessons() -> None:
    """Підтипи є різновидами базового класу."""
    assert isinstance(make_lesson(Lecture), Lesson)
    assert isinstance(make_lesson(Practice), Lesson)


def test_room_load_is_frozen_and_comparable() -> None:
    """RoomLoad незмінний, рівність за значенням."""
    load = RoomLoad(room=101, lessons=2, need=3)

    with pytest.raises(dataclasses.FrozenInstanceError):
        load.need = 5  # type: ignore[misc]
    assert load == RoomLoad(101, 2, 3)
    assert load != RoomLoad(101, 2, 4)
    assert hash(load) == hash(RoomLoad(101, 2, 3))


def test_summary_is_frozen() -> None:
    """ScheduleSummary не можна змінити після створення."""
    summary = ScheduleSummary(1, "Понеділок", 1, (("Т", 1),), (1,), (1, 1), ())

    with pytest.raises(dataclasses.FrozenInstanceError):
        summary.total = 5  # type: ignore[misc]


def test_summary_equality_and_repr() -> None:
    """Dataclass дає рівність і repr автоматично."""
    first = ScheduleSummary(0, "Середа", 0, (), (), None, ())
    second = ScheduleSummary(0, "Середа", 0, (), (), None, ())

    assert first == second
    assert "ScheduleSummary(total=0" in repr(first)


class FakeSeminar:
    """Не є Lesson, але має ``room`` і ``room_need`` (качина типізація)."""

    def __init__(self, room: int, need: int) -> None:
        """Створює об'єкт із потрібним протоколу інтерфейсом."""
        self.room = room
        self._need = need

    def room_need(self) -> int:
        """Повертає потребу в аудиторії."""
        return self._need


def test_analysis_works_with_any_object_matching_protocol() -> None:
    """room_loads не перевіряє клас: достатньо протоколу."""
    items = [FakeSeminar(7, 3), FakeSeminar(7, 1), FakeSeminar(2, 2)]

    assert room_loads(items) == (RoomLoad(2, 1, 2), RoomLoad(7, 2, 4))

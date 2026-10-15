"""Обчислення над об'єктами розкладу через спільний протокол."""

from collections.abc import Sequence

from kzp_lab07.models import Lesson, NeedsRoom, RoomLoad, ScheduleSummary


def filter_by_day(lessons: Sequence[Lesson], day: str) -> list[Lesson]:
    """Відбирає заняття заданого дня (без урахування регістру)."""
    wanted = day.strip().casefold()
    return [lesson for lesson in lessons if lesson.day.casefold() == wanted]


def count_by_teacher(lessons: Sequence[Lesson]) -> dict[str, int]:
    """Рахує заняття за викладачем; ключі відсортовано для стабільного звіту."""
    teachers = {lesson.teacher for lesson in lessons}
    return {
        teacher: sum(1 for lesson in lessons if lesson.teacher == teacher)
        for teacher in sorted(teachers)
    }


def unique_rooms(lessons: Sequence[NeedsRoom]) -> set[int]:
    """Повертає множину аудиторій без повторів."""
    return {lesson.room for lesson in lessons}


def period_bounds(lessons: Sequence[Lesson]) -> tuple[int, int] | None:
    """Повертає першу й останню пару або ``None`` для порожнього набору."""
    if not lessons:
        return None
    periods = [lesson.period for lesson in lessons]
    return min(periods), max(periods)


def room_loads(lessons: Sequence[NeedsRoom]) -> tuple[RoomLoad, ...]:
    """Підсумовує завантаження аудиторій через ``room_need``.

    Функція знає лише про протокол ``NeedsRoom``: нові підтипи не потребують змін.
    """
    rooms = sorted(unique_rooms(lessons))
    return tuple(
        RoomLoad(
            room=room,
            lessons=sum(1 for lesson in lessons if lesson.room == room),
            need=sum(lesson.room_need() for lesson in lessons if lesson.room == room),
        )
        for room in rooms
    )


def make_summary(lessons: Sequence[Lesson], day: str) -> ScheduleSummary:
    """Збирає незмінний підсумок: всі записи, заняття дня, викладачі, аудиторії."""
    selected = filter_by_day(lessons, day)
    return ScheduleSummary(
        total=len(lessons),
        day=day.strip(),
        lessons=len(selected),
        teachers=tuple(count_by_teacher(selected).items()),
        rooms=tuple(sorted(unique_rooms(selected))),
        bounds=period_bounds(selected),
        room_loads=room_loads(selected),
    )

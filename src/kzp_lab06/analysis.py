"""Обчислення над записами розкладу: відбір, агрегування, множини."""

from kzp_lab06.loader import LessonRecord

NUMERIC_METRICS = ("period", "room")


def filter_by_day(records: list[LessonRecord], day: str) -> list[LessonRecord]:
    """Відбирає заняття заданого дня (без урахування регістру)."""
    wanted = day.strip().casefold()
    return [record for record in records if record["day"].casefold() == wanted]


def count_by_teacher(records: list[LessonRecord]) -> dict[str, int]:
    """Рахує заняття за викладачем; ключі відсортовано для стабільного звіту."""
    teachers = {record["teacher"] for record in records}
    return {
        teacher: sum(1 for record in records if record["teacher"] == teacher)
        for teacher in sorted(teachers)
    }


def unique_rooms(records: list[LessonRecord]) -> set[int]:
    """Повертає множину аудиторій без повторів."""
    return {record["room"] for record in records}


def period_bounds(records: list[LessonRecord]) -> tuple[int, int] | None:
    """Повертає першу й останню пару або ``None`` для порожнього набору."""
    if not records:
        return None
    periods = [record["period"] for record in records]
    return min(periods), max(periods)


def summarize(
    records: list[LessonRecord],
    *metrics: str,
    minimum_period: int = 0,
    **labels: str,
) -> dict[str, float]:
    """Обчислює суми вибраних числових полів після відбору за парою.

    ``metrics`` — назви полів (``period`` або ``room``), ``minimum_period`` —
    найменший номер пари, що береться до розрахунку, ``labels`` — підписи
    результатів за назвою метрики. Невідома метрика — ``ValueError``.
    """
    for metric in metrics:
        if metric not in NUMERIC_METRICS:
            raise ValueError(f"Невідома метрика: {metric}")
    selected = [record for record in records if record["period"] >= minimum_period]
    result: dict[str, float] = {"count": float(len(selected))}
    for metric in metrics:
        result[labels.get(metric, metric)] = float(
            sum(record[metric] for record in selected)
        )
    return result


def make_summary(records: list[LessonRecord], day: str) -> dict[str, object]:
    """Збирає підсумок для звіту: всі записи, заняття дня, викладачі, аудиторії."""
    selected = filter_by_day(records, day)
    return {
        "total": len(records),
        "day": day.strip(),
        "lessons": int(summarize(selected)["count"]),
        "teachers": count_by_teacher(selected),
        "rooms": sorted(unique_rooms(selected)),
        "bounds": period_bounds(selected),
    }

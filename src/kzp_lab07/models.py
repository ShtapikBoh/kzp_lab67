"""Об'єктна модель розкладу: заняття, підтипи, підсумок і протокол."""

from dataclasses import dataclass
from typing import Protocol

LECTURE_MIN_ROOM = 200


class NeedsRoom(Protocol):
    """Протокол об'єкта, що займає аудиторію й знає свою потребу в ній."""

    @property
    def room(self) -> int:
        """Повертає номер аудиторії."""
        ...

    def room_need(self) -> int:
        """Повертає потребу в аудиторії (аудиторні години)."""
        ...


class Lesson:
    """Базове заняття: спільний стан, перевірки й контракт ``room_need``."""

    def __init__(
        self, subject: str, teacher: str, day: str, period: int, room: int
    ) -> None:
        """Створює заняття; кожне значення проходить перевірку у властивості."""
        self.subject = subject
        self.teacher = teacher
        self.day = day
        self.period = period
        self.room = room

    @staticmethod
    def _text(name: str, value: str) -> str:
        """Перевіряє, що текстове значення непорожнє, і обрізає пробіли."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Поле {name} не може бути порожнім")
        return value.strip()

    @staticmethod
    def _positive(name: str, value: int) -> int:
        """Перевіряє, що значення — ціле число більше 0."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"Поле {name} має бути цілим числом")
        if value <= 0:
            raise ValueError(f"Поле {name} має бути більшим за 0")
        return value

    @property
    def subject(self) -> str:
        """Повертає назву предмета."""
        return self._subject

    @subject.setter
    def subject(self, value: str) -> None:
        """Встановлює непорожню назву предмета."""
        self._subject = self._text("subject", value)

    @property
    def teacher(self) -> str:
        """Повертає викладача."""
        return self._teacher

    @teacher.setter
    def teacher(self, value: str) -> None:
        """Встановлює непорожнє ім'я викладача."""
        self._teacher = self._text("teacher", value)

    @property
    def day(self) -> str:
        """Повертає день тижня."""
        return self._day

    @day.setter
    def day(self, value: str) -> None:
        """Встановлює непорожній день тижня."""
        self._day = self._text("day", value)

    @property
    def period(self) -> int:
        """Повертає номер пари."""
        return self._period

    @period.setter
    def period(self, value: int) -> None:
        """Встановлює номер пари (ціле число більше 0)."""
        # Записуємо у внутрішнє поле, щоб setter не викликав сам себе.
        self._period = self._positive("period", value)

    @property
    def room(self) -> int:
        """Повертає номер аудиторії."""
        return self._room

    @room.setter
    def room(self, value: int) -> None:
        """Встановлює номер аудиторії (ціле число більше 0)."""
        self._room = self._positive("room", value)

    def room_need(self) -> int:
        """Оголошує спільну операцію: потреба в аудиторії для підтипів."""
        raise NotImplementedError

    @property
    def sort_key(self) -> tuple[int, int, str]:
        """Повертає ключ впорядкування: пара, аудиторія, предмет."""
        return (self.period, self.room, self.subject)

    def _identity(self) -> tuple[str, str, str, str, int, int]:
        """Повертає значення, за якими порівнюються заняття."""
        return (
            type(self).__name__,
            self.subject,
            self.teacher,
            self.day,
            self.period,
            self.room,
        )

    def __str__(self) -> str:
        """Повертає коротке подання для читача."""
        return (
            f"{self.subject} ({self.teacher}, {self.day}, "
            f"пара {self.period}, ауд. {self.room})"
        )

    def __repr__(self) -> str:
        """Повертає діагностичне подання об'єкта."""
        return (
            f"{type(self).__name__}(subject={self.subject!r}, "
            f"teacher={self.teacher!r}, day={self.day!r}, "
            f"period={self.period!r}, room={self.room!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Порівнює заняття за типом і всіма полями."""
        if not isinstance(other, Lesson):
            return NotImplemented
        return self._identity() == other._identity()

    def __lt__(self, other: object) -> bool:
        """Впорядковує заняття за ``sort_key``."""
        if not isinstance(other, Lesson):
            return NotImplemented
        return self.sort_key < other.sort_key

    # Об'єкт змінюваний (є setter-и), тому він не має бути ключем словника.
    __hash__ = None  # type: ignore[assignment]


class Lecture(Lesson):
    """Лекція: займає аудиторію дві академічні години (одна пара)."""

    def room_need(self) -> int:
        """Повертає потребу в аудиторії: 2 години."""
        return 2


class Practice(Lesson):
    """Практичне заняття: займає аудиторію одну академічну годину."""

    def room_need(self) -> int:
        """Повертає потребу в аудиторії: 1 година."""
        return 1


@dataclass(frozen=True)
class RoomLoad:
    """Завантаження однієї аудиторії."""

    room: int
    lessons: int
    need: int


@dataclass(frozen=True)
class ScheduleSummary:
    """Незмінний підсумок розкладу для звіту."""

    total: int
    day: str
    lessons: int
    teachers: tuple[tuple[str, int], ...]
    rooms: tuple[int, ...]
    bounds: tuple[int, int] | None
    room_loads: tuple[RoomLoad, ...]

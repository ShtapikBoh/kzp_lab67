# kzp_lab67 — розклад занять засобами Python

Лабораторні роботи № 6–7 з курсу «Кросплатформні засоби програмування»,
варіант **№ 3 — Розклад занять**.

- **Лабораторна № 6** — пакет `kzp_lab06`: CSV → словникові записи → звіт.
- **Лабораторна № 7** — пакет `kzp_lab07`: ті самі дані як об'єкти з власною
  поведінкою (`Lesson`, `Lecture`, `Practice`), незмінний `@dataclass`, протокол.

Документи лабораторної № 6 збережено в теці [`lab06_docs/`](lab06_docs/).

## Призначення

Пакет читає CSV-файл розкладу занять, перетворює рядки на типізовані значення
(лаб. 6) або на об'єкти зі спільною поведінкою (лаб. 7), будує звіт і записує
його в текстовий файл. Вхідний файл не змінюється.

## Формат вхідних даних

CSV у UTF-8, роздільник — кома, перший рядок — заголовок із машинними назвами.
Читання йде за назвами стовпців, порядок не важливий.

```
day,period,room,subject,teacher
Понеділок,1,101,Програмування,Олексів М. В.
Вівторок,1,215,Кросплатформні засоби,Рудик Ю. І.
Середа,1,98,Бази даних,Коваленко О. П.
```

| Поле | Тип | Правило |
|------|-----|---------|
| `subject`, `teacher`, `day` | текст | непорожні |
| `period` (номер пари), `room` (аудиторія) | ціле | більше 0 |

Поле з комою, лапками чи переносом рядка береться в лапки. Файл лише із
заголовком — коректний порожній вхід, повністю порожній файл — помилка.

## Структура

```
src/kzp_lab06/    # лаб. 6: словники
src/kzp_lab07/    # лаб. 7: об'єкти
├── __init__.py   # публічний API
├── errors.py     # DataError
├── models.py     # Lesson, Lecture, Practice, RoomLoad, ScheduleSummary, NeedsRoom
├── loader.py     # CSV → об'єкти, вибір підтипу
├── analysis.py   # відбір, словник, множина, завантаження аудиторій
├── reporting.py  # формування й запис звіту
└── cli.py        # аргументи, коди завершення
tests/            # pytest (139 тестів)
data/input.csv    # вхідні дані
lab06_docs/       # README і REPORT лабораторної № 6
```

### Модель лабораторної № 7

- `Lesson` — базовий клас: `@property` із setter-валідацією для `subject`,
  `teacher`, `day`, `period`, `room`; `__str__`, `__repr__`, `__eq__`,
  `__lt__`, `sort_key`; спільна операція `room_need()`.
- `Lecture` (2 аудиторні години) і `Practice` (1 година) по-різному реалізують
  `room_need()`.
- `RoomLoad` і `ScheduleSummary` — `@dataclass(frozen=True)`.
- `NeedsRoom` — `Protocol`; `analysis` працює через нього без перевірок класу.

## Запуск

Потрібен Python 3.11 або новіший.

```
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"

python -m kzp_lab07.cli data/input.csv reports/summary.txt
python -m kzp_lab07.cli data/input.csv reports/summary.txt --day Середа
kzp-lab07 data/input.csv reports/summary.txt
kzp-lab06 data/input.csv reports/summary.txt     # лаб. 6
```

| Код | Значення |
|-----|----------|
| `0` | успіх |
| `1` | помилка даних (`DataError`) |
| `2` | хибні аргументи |
| `3` | помилка файла |

Повідомлення про помилки виводяться в stderr.

## Приклад звіту (лабораторна № 7)

```
Записів у файлі: 3
День: Понеділок
Занять у цей день: 1
Заняття за викладачами:
  Олексів М. В.: 1
Аудиторії: 101
Перша пара: 1
Остання пара: 1
Завантаження аудиторій:
  101: 1 зан., 1 год
```

Перші дев'ять рядків збігаються зі звітом лабораторної № 6; додано блок
«Завантаження аудиторій».

## Перевірка

```
python -m pytest
ruff check .
ruff format --check .
python -m build
```

Wheel у чистому середовищі (Ubuntu і macOS):

```
python3 -m venv .venv-wheel
.venv-wheel/bin/python -m pip install --no-deps dist/kzp_lab67-1.1.0-py3-none-any.whl
.venv-wheel/bin/python -m kzp_lab07.cli data/input.csv reports/wheel-summary.txt
```

На Windows замість `.venv-wheel/bin/python` використовується
`.venv-wheel\Scripts\python`.

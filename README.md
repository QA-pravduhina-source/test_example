[![Build Status](https://github.com/QA-pravduhina-source/test_example/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/QA-pravduhina-source/test_example/actions/workflows/python-tests.yml)

# Кредитный калькулятор-скоринг

Демо-проект для автоматизации принятия решений по кредитным заявкам: расчёт скоринга, REST API на FastAPI, пакетная обработка заявок, автотесты (включая проверки безопасности) и фабрика тестовых сущностей для ручной проверки.

---

## О проекте

Система оценивает заявку клиента по двум параметрам — **ежемесячному доходу** и **желаемой сумме кредита** — и возвращает одно из решений:

- **Одобрено** — заявка проходит все проверки;
- **Отказ** — доход ниже лимита или сумма кредита слишком велика;
- **Ошибка** — некорректные отрицательные значения.

Логика скоринга сосредоточена в одном месте (`main.py`), поэтому её используют и консольный сценарий, и модуль заявок, и HTTP API.

### Возможности

| Компонент | Назначение |
|-----------|------------|
| `main.py` | Ядро скоринга и безопасный разбор ввода (`parse_positive_int`) |
| `database.py` | Список заявок и пакетная обработка через `process_all_applications()` |
| `app.py` | REST API: `POST /api/v1/scoring` |
| `test.py` | Автотесты скоринга, валидации и безопасности ввода |
| `test_database.py` | Тесты обработки заявок и консистентности данных |
| `test_generate_entities.py` | Фабрика заёмщиков и заявок → `generated_test_data.json` |

### Правила скоринга

1. Доход **≥ 150 000** ₽ (иначе отказ).
2. Сумма кредита **≤ доход × 5** (иначе отказ).
3. Отрицательный доход или сумма → сообщение об ошибке.

---

## Структура проекта

```
python_course/
├── main.py                    # credit_scoring, parse_positive_int
├── database.py                # loan_applications, process_all_applications
├── app.py                     # FastAPI-приложение
├── Dockerfile                 # образ для запуска API в контейнере
├── docker-compose.yml         # PostgreSQL + FastAPI (db + web)
├── .github/workflows/         # CI: GitHub Actions (python-tests.yml)
├── test.py                    # тесты скоринга и безопасности
├── test_database.py           # тесты базы заявок
├── test_generate_entities.py  # генерация сущностей для ручных тестов
├── generated_test_data.json   # создаётся после test_generate_entities.py
└── README.md
```

---

## Установка зависимостей

```bash
pip install fastapi uvicorn pydantic
```

Python 3.10+ рекомендуется (используются аннотации типов).

---

## Запуск API-сервера

Из корня проекта:

```bash
python -m uvicorn app:app --reload
```

После старта:

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Пример запроса** (`POST /api/v1/scoring`):

```json
{
  "income": 200000,
  "loan_amount": 500000
}
```

**Пример ответа:**

```json
{
  "status": "Одобрено! Кредит на сумму 500000 успешно согласован."
}
```

---

## Запуск в Docker

Сборка образа из корня проекта:

```bash
docker build -t credit-scoring-api .
```

Запуск контейнера (порт 8000):

```bash
docker run -p 8000:8000 credit-scoring-api
```

После старта API доступен по адресу [http://127.0.0.1:8000](http://127.0.0.1:8000), документация — [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

В образе используется `python:3.12-slim`; зависимости (`fastapi`, `uvicorn`, `pydantic`) устанавливаются при сборке. Сервер слушает `0.0.0.0:8000` внутри контейнера.

### Запуск через Docker Compose

Поднимает PostgreSQL (`fintech_db`) и API (`fintech_web_app`) одной командой:

```bash
docker compose up --build
```

В фоновом режиме:

```bash
docker compose up --build -d
```

Остановка и удаление контейнеров:

```bash
docker compose down
```

| Сервис | Контейнер | Порт | Описание |
|--------|-----------|------|----------|
| `db` | `fintech_db` | 5432 | PostgreSQL 15, БД `fintech_database` |
| `web` | `fintech_web_app` | 8000 | FastAPI, `DATABASE_URL` → `db:5432` |

Данные PostgreSQL сохраняются в именованном томе `postgres_data` (`/var/lib/postgresql/data` в контейнере).

После старта: API — [http://127.0.0.1:8000](http://127.0.0.1:8000), Swagger — [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Запуск автотестов

Все тесты используют стандартный модуль `unittest`.

**Скоринг и безопасность ввода:**

```bash
python test.py
```

или

```bash
python -m unittest test -v
```

**Обработка заявок в `database.py`:**

```bash
python test_database.py
```

**Генерация заёмщиков и заявок** (для ручного тестирования; создаёт `generated_test_data.json`):

```bash
python test_generate_entities.py
```

**Все тесты одной командой:**

```bash
python -m unittest discover -v
```

Та же команда выполняется автоматически в **GitHub Actions** при каждом push в ветку `main` (workflow `python-tests.yml`).

---

## Дополнительно

**Консольный скоринг** (интерактивный ввод):

```bash
python main.py
```

**Просмотр заявок с результатами скоринга:**

```bash
python database.py
```

**Фабрика сущностей** формирует согласованные пары «заёмщик ↔ заявка», в том числе заёмщика **без заявок**, и сохраняет готовые примеры для Swagger и Postman в `generated_test_data.json`.

---

## Автор

Анна Александрова

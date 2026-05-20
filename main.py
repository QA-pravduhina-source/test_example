import logging
import os
import sys

MAX_MONEY_INPUT_LEN = 15

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def log_database_error(message: str, exc: BaseException | None = None) -> None:
    """Логирование ошибок при работе с данными заявок / БД."""
    if exc is not None:
        logger.error("%s: %s", message, exc, exc_info=True)
    else:
        logger.error(message)


def parse_positive_int(raw: str, *, field_name: str) -> int:
    """
    Разбор целого неотрицательного числа из строки ввода.
    Только ASCII-цифры после strip — отсекаем нечисловой ввод и типичные вредоносные вставки.
    """
    if not isinstance(raw, str):
        raise TypeError("Ожидается строка.")
    s = raw.strip()
    if not s:
        raise ValueError(f"{field_name}: пустой ввод.")
    if len(s) > MAX_MONEY_INPUT_LEN:
        raise ValueError(f"{field_name}: значение слишком длинное.")
    if not all("0" <= c <= "9" for c in s):
        raise ValueError(f"{field_name}: допускаются только целые неотрицательные числа (цифры 0–9).")
    return int(s)


def credit_scoring(income: int, loan_amount: int) -> str:
    logger.info(
        "Запрос на скоринг: income=%s, loan_amount=%s",
        income,
        loan_amount,
    )
    if income < 0:
        decision = "Ошибка: доход не может быть отрицательным."
        logger.warning("Скоринг завершён с ошибкой: %s", decision)
        return decision
    if loan_amount < 0:
        decision = "Ошибка: сумма кредита не может быть отрицательной."
        logger.warning("Скоринг завершён с ошибкой: %s", decision)
        return decision
    if income < 150000:
        decision = "Отказ: ваш доход ниже минимального лимита."
        logger.info("Решение по скорингу: %s", decision)
        return decision
    if loan_amount > income * 5:
        decision = "Отказ: запрошенная сумма слишком велика для вашего дохода."
        logger.info("Решение по скорингу: %s", decision)
        return decision
    decision = f"Одобрено! Кредит на сумму {loan_amount} успешно согласован."
    logger.info("Решение по скорингу: одобрено, сумма=%s", loan_amount)
    return decision


def check_database_url_configured() -> bool:
    """Проверка наличия DATABASE_URL (для Docker / production)."""
    url = os.getenv("DATABASE_URL")
    if not url:
        log_database_error("DATABASE_URL не задан — подключение к PostgreSQL недоступно")
        return False
    if not url.startswith("postgresql://"):
        log_database_error(f"Некорректный формат DATABASE_URL: {url[:20]}...")
        return False
    logger.info("DATABASE_URL задан, хост БД доступен в конфигурации")
    return True


if __name__ == "__main__":
    try:
        income = parse_positive_int(
            input("Введите ваш ежемесячный доход: "),
            field_name="Доход",
        )
        loan_amount = parse_positive_int(
            input("Введите желаемую сумму кредита: "),
            field_name="Сумма кредита",
        )
    except ValueError as exc:
        logger.error("Ошибка ввода: %s", exc)
        print(f"Ошибка ввода: {exc}")
        raise SystemExit(1) from exc
    print(credit_scoring(income, loan_amount))

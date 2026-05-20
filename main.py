MAX_MONEY_INPUT_LEN = 15


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
    if income < 0:
        return "Ошибка: доход не может быть отрицательным."
    if loan_amount < 0:
        return "Ошибка: сумма кредита не может быть отрицательной."
    if income < 150000:
        return "Отказ: ваш доход ниже минимального лимита."
    if loan_amount > income * 5:
        return "Отказ: запрошенная сумма слишком велика для вашего дохода."
    return f"Одобрено! Кредит на сумму {loan_amount} успешно согласован."


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
        print(f"Ошибка ввода: {exc}")
        raise SystemExit(1) from exc
    print(credit_scoring(income, loan_amount))

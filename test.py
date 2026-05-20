import unittest

from main import MAX_MONEY_INPUT_LEN, credit_scoring, parse_positive_int


class TestCreditScoring(unittest.TestCase):
    def test_reject_low_income(self):
        self.assertEqual(
            credit_scoring(149_999, 1),
            "Отказ: ваш доход ниже минимального лимита.",
        )

    def test_reject_too_big_loan(self):
        self.assertEqual(
            credit_scoring(150_000, 150_000 * 5 + 1),
            "Отказ: запрошенная сумма слишком велика для вашего дохода.",
        )

    def test_approve_when_all_conditions_pass(self):
        self.assertEqual(
            credit_scoring(200_000, 500_000),
            "Одобрено! Кредит на сумму 500000 успешно согласован.",
        )

    def test_boundary_income_is_allowed(self):
        self.assertEqual(
            credit_scoring(150_000, 1),
            "Одобрено! Кредит на сумму 1 успешно согласован.",
        )

    def test_boundary_loan_equal_income_times_5_is_allowed(self):
        self.assertEqual(
            credit_scoring(160_000, 160_000 * 5),
            "Одобрено! Кредит на сумму 800000 успешно согласован.",
        )

    def test_reject_negative_income(self):
        self.assertEqual(
            credit_scoring(-1, 100_000),
            "Ошибка: доход не может быть отрицательным.",
        )

    def test_reject_negative_loan(self):
        self.assertEqual(
            credit_scoring(200_000, -1),
            "Ошибка: сумма кредита не может быть отрицательной.",
        )


class TestParsePositiveInt(unittest.TestCase):
    def test_accepts_digits_and_strips_spaces(self):
        self.assertEqual(parse_positive_int("  150000  ", field_name="Доход"), 150_000)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError) as ctx:
            parse_positive_int("", field_name="Доход")
        self.assertIn("пустой", str(ctx.exception).lower())

    def test_rejects_non_numeric_letters(self):
        with self.assertRaises(ValueError):
            parse_positive_int("abc", field_name="Доход")

    def test_rejects_float_like_string(self):
        with self.assertRaises(ValueError):
            parse_positive_int("150000.50", field_name="Доход")

    def test_rejects_minus_sign_even_if_digits_follow(self):
        with self.assertRaises(ValueError):
            parse_positive_int("-100", field_name="Доход")


class TestInputSecurity(unittest.TestCase):
    """Проверки на типичные вредоносные/некорректные вставки вместо числа."""

    def test_rejects_command_injection_like_string(self):
        with self.assertRaises(ValueError):
            parse_positive_int("; rm -rf /", field_name="Доход")

    def test_rejects_newline_injection(self):
        with self.assertRaises(ValueError):
            parse_positive_int("100\n200", field_name="Доход")

    def test_rejects_python_expression(self):
        with self.assertRaises(ValueError):
            parse_positive_int("__import__('os')", field_name="Доход")

    def test_rejects_hex_notation(self):
        with self.assertRaises(ValueError):
            parse_positive_int("0x10", field_name="Доход")

    def test_rejects_oversized_input_length(self):
        too_long = "1" * (MAX_MONEY_INPUT_LEN + 1)
        with self.assertRaises(ValueError) as ctx:
            parse_positive_int(too_long, field_name="Доход")
        self.assertIn("длинн", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)

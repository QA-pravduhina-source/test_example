import copy
import unittest

import database
from database import loan_applications, process_all_applications
from main import credit_scoring

SEED_APPLICATIONS = [
    {
        "id": 1,
        "client_name": "Аня",
        "income": 150_000,
        "loan_amount": 500_000,
    },
    {
        "id": 2,
        "client_name": "Игорь",
        "income": 220_000,
        "loan_amount": 800_000,
    },
    {
        "id": 3,
        "client_name": "Мария",
        "income": 95_000,
        "loan_amount": 200_000,
    },
]

REQUIRED_KEYS = ("id", "client_name", "income", "loan_amount")


def _reset_loan_applications() -> None:
    loan_applications.clear()
    for app in copy.deepcopy(SEED_APPLICATIONS):
        app.pop("status", None)
        loan_applications.append(app)


def _find_by_id(app_id: int) -> dict:
    for app in loan_applications:
        if app["id"] == app_id:
            return app
    raise AssertionError(f"Заявка с id={app_id} не найдена")


class TestProcessAllApplications(unittest.TestCase):
    def setUp(self) -> None:
        _reset_loan_applications()

    def test_all_applications_get_status_key(self) -> None:
        process_all_applications()
        for app in loan_applications:
            self.assertIn("status", app)
            self.assertIsInstance(app["status"], str)
            self.assertTrue(app["status"])

    def test_maria_status_contains_otkaz(self) -> None:
        process_all_applications()
        maria = _find_by_id(3)
        self.assertEqual(maria["client_name"], "Мария")
        self.assertIn("Отказ", maria["status"])

    def test_anya_status_contains_odobreno(self) -> None:
        process_all_applications()
        anya = _find_by_id(1)
        self.assertEqual(anya["client_name"], "Аня")
        self.assertIn("Одобрено", anya["status"])

    def test_igor_status_contains_odobreno(self) -> None:
        process_all_applications()
        igor = _find_by_id(2)
        self.assertEqual(igor["client_name"], "Игорь")
        self.assertIn("Одобрено", igor["status"])

    def test_status_matches_credit_scoring_for_each_client(self) -> None:
        process_all_applications()
        for app in loan_applications:
            expected = credit_scoring(app["income"], app["loan_amount"])
            self.assertEqual(app["status"], expected)


class TestLoanApplicationsDataConsistency(unittest.TestCase):
    def setUp(self) -> None:
        _reset_loan_applications()

    def test_seed_has_three_applications(self) -> None:
        self.assertEqual(len(loan_applications), 3)

    def test_each_application_has_required_keys(self) -> None:
        for app in loan_applications:
            for key in REQUIRED_KEYS:
                self.assertIn(key, app)

    def test_field_types_are_correct(self) -> None:
        for app in loan_applications:
            self.assertIsInstance(app["id"], int)
            self.assertIsInstance(app["client_name"], str)
            self.assertIsInstance(app["income"], int)
            self.assertIsInstance(app["loan_amount"], int)

    def test_ids_are_unique(self) -> None:
        ids = [app["id"] for app in loan_applications]
        self.assertEqual(len(ids), len(set(ids)))

    def test_seed_amounts_are_non_negative(self) -> None:
        for app in loan_applications:
            self.assertGreaterEqual(app["income"], 0)
            self.assertGreaterEqual(app["loan_amount"], 0)

    def test_processing_does_not_remove_original_fields(self) -> None:
        process_all_applications()
        for app in loan_applications:
            for key in REQUIRED_KEYS:
                self.assertIn(key, app)

    def test_reprocessing_overwrites_status_consistently(self) -> None:
        process_all_applications()
        first_pass = {app["id"]: app["status"] for app in loan_applications}
        process_all_applications()
        second_pass = {app["id"]: app["status"] for app in loan_applications}
        self.assertEqual(first_pass, second_pass)


class TestLoanApplicationsSecurity(unittest.TestCase):
    def setUp(self) -> None:
        _reset_loan_applications()

    def test_status_is_plain_string_not_callable(self) -> None:
        process_all_applications()
        for app in loan_applications:
            status = app["status"]
            self.assertIsInstance(status, str)
            self.assertFalse(callable(status))

    def test_status_does_not_echo_untrusted_client_name(self) -> None:
        loan_applications.append(
            {
                "id": 99,
                "client_name": "<script>alert(1)</script>",
                "income": 200_000,
                "loan_amount": 100_000,
            }
        )
        process_all_applications()
        suspicious = _find_by_id(99)
        self.assertNotIn("<script>", suspicious["status"])
        self.assertIn("Одобрено", suspicious["status"])

    def test_negative_income_gets_error_status_not_approval(self) -> None:
        loan_applications.append(
            {
                "id": 100,
                "client_name": "Тест",
                "income": -1,
                "loan_amount": 10_000,
            }
        )
        process_all_applications()
        test_app = _find_by_id(100)
        self.assertIn("Ошибка", test_app["status"])
        self.assertNotIn("Одобрено", test_app["status"])

    def test_negative_loan_gets_error_status_not_approval(self) -> None:
        loan_applications.append(
            {
                "id": 101,
                "client_name": "Тест",
                "income": 200_000,
                "loan_amount": -1,
            }
        )
        process_all_applications()
        test_app = _find_by_id(101)
        self.assertIn("Ошибка", test_app["status"])
        self.assertNotIn("Одобрено", test_app["status"])

    def test_processing_empty_list_does_not_crash(self) -> None:
        loan_applications.clear()
        process_all_applications()
        self.assertEqual(loan_applications, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""
Генерация согласованных заёмщиков и заявок для ручного тестирования.

Запуск:
    python test_generate_entities.py

Результат сохраняется в generated_test_data.json в корне проекта.
"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any

from main import credit_scoring

OUTPUT_FILE = Path(__file__).resolve().parent / "generated_test_data.json"

_borrower_id = 1000
_application_id = 5000


def _next_borrower_id() -> int:
    global _borrower_id
    _borrower_id += 1
    return _borrower_id


def _next_application_id() -> int:
    global _application_id
    _application_id += 1
    return _application_id


def make_borrower(name: str, income: int, *, borrower_id: int | None = None) -> dict[str, Any]:
    if income < 0:
        raise ValueError("Доход заёмщика не может быть отрицательным.")
    return {
        "id": borrower_id if borrower_id is not None else _next_borrower_id(),
        "name": name,
        "income": income,
    }


def make_application(borrower: dict[str, Any], loan_amount: int, *, application_id: int | None = None) -> dict[str, Any]:
    if loan_amount < 0:
        raise ValueError("Сумма кредита не может быть отрицательной.")
    status = credit_scoring(borrower["income"], loan_amount)
    return {
        "id": application_id if application_id is not None else _next_application_id(),
        "borrower_id": borrower["id"],
        "client_name": borrower["name"],
        "income": borrower["income"],
        "loan_amount": loan_amount,
        "status": status,
    }


def assert_borrower_application_consistent(borrower: dict[str, Any], application: dict[str, Any]) -> None:
    assert application["borrower_id"] == borrower["id"]
    assert application["client_name"] == borrower["name"]
    assert application["income"] == borrower["income"]
    assert application["status"] == credit_scoring(borrower["income"], application["loan_amount"])


class TestDataCatalog:
    """Накопитель сущностей для экспорта после прогона тестов."""

    def __init__(self) -> None:
        self.borrowers: list[dict[str, Any]] = []
        self.applications: list[dict[str, Any]] = []

    def add_borrower(self, borrower: dict[str, Any], applications: list[dict[str, Any]] | None = None) -> None:
        apps = applications or []
        for app in apps:
            assert_borrower_application_consistent(borrower, app)
        self.borrowers.append(copy.deepcopy(borrower))
        self.applications.extend(copy.deepcopy(apps))

    def to_export_dict(self) -> dict[str, Any]:
        by_borrower: dict[int, list[dict[str, Any]]] = {b["id"]: [] for b in self.borrowers}
        for app in self.applications:
            by_borrower[app["borrower_id"]].append(app)

        borrowers_export = []
        for borrower in self.borrowers:
            borrowers_export.append(
                {
                    **borrower,
                    "applications": by_borrower[borrower["id"]],
                }
            )

        without_apps = [b for b in borrowers_export if not b["applications"]]

        return {
            "borrowers": borrowers_export,
            "applications": self.applications,
            "borrowers_without_applications": without_apps,
            "api_examples": self._api_examples(),
        }

    def _api_examples(self) -> list[dict[str, Any]]:
        examples = []
        for app in self.applications:
            examples.append(
                {
                    "description": f"Заявка №{app['id']} ({app['client_name']})",
                    "post_body": {
                        "income": app["income"],
                        "loan_amount": app["loan_amount"],
                    },
                    "expected_status_contains": (
                        "Одобрено" if "Одобрено" in app["status"] else "Отказ" if "Отказ" in app["status"] else "Ошибка"
                    ),
                }
            )
        return examples

    def save(self, path: Path = OUTPUT_FILE) -> Path:
        payload = self.to_export_dict()
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


catalog = TestDataCatalog()


class TestGenerateEntities(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        catalog.borrowers.clear()
        catalog.applications.clear()

    def test_generate_approved_borrower_with_application(self) -> None:
        borrower = make_borrower("Аня (тест)", 200_000)
        application = make_application(borrower, 500_000)
        assert_borrower_application_consistent(borrower, application)
        self.assertIn("Одобрено", application["status"])
        catalog.add_borrower(borrower, [application])

    def test_generate_rejected_low_income_borrower(self) -> None:
        borrower = make_borrower("Мария (тест)", 95_000)
        application = make_application(borrower, 200_000)
        assert_borrower_application_consistent(borrower, application)
        self.assertIn("Отказ", application["status"])
        catalog.add_borrower(borrower, [application])

    def test_generate_rejected_loan_too_high(self) -> None:
        borrower = make_borrower("Игорь (тест)", 150_000)
        application = make_application(borrower, 150_000 * 5 + 1)
        assert_borrower_application_consistent(borrower, application)
        self.assertIn("Отказ", application["status"])
        catalog.add_borrower(borrower, [application])

    def test_generate_borrower_with_multiple_consistent_applications(self) -> None:
        borrower = make_borrower("Ольга (тест)", 300_000)
        app1 = make_application(borrower, 100_000)
        app2 = make_application(borrower, 1_000_000)
        for app in (app1, app2):
            assert_borrower_application_consistent(borrower, app)
        catalog.add_borrower(borrower, [app1, app2])
        self.assertEqual(len([a for a in catalog.applications if a["borrower_id"] == borrower["id"]]), 2)

    def test_generate_borrower_without_applications(self) -> None:
        borrower = make_borrower("Пётр (без заявок)", 180_000)
        catalog.add_borrower(borrower, [])
        self.assertEqual(
            [b for b in catalog.borrowers if b["id"] == borrower["id"]][0]["id"],
            borrower["id"],
        )
        linked = [a for a in catalog.applications if a["borrower_id"] == borrower["id"]]
        self.assertEqual(linked, [])

    @classmethod
    def tearDownClass(cls) -> None:
        path = catalog.save()
        print(f"\n[test_generate_entities] Данные для ручных тестов: {path}")
        print(f"  Заёмщиков: {len(catalog.borrowers)}")
        print(f"  Заявок: {len(catalog.applications)}")
        print(
            f"  Без заявок: {len(catalog.to_export_dict()['borrowers_without_applications'])}"
        )


class TestGeneratedExportIntegrity(unittest.TestCase):
    def test_export_file_exists_and_is_valid_json(self) -> None:
        if not OUTPUT_FILE.exists():
            self.skipTest("Сначала запустите TestGenerateEntities (python test_generate_entities.py)")
        data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        self.assertIn("borrowers", data)
        self.assertIn("applications", data)
        self.assertIn("borrowers_without_applications", data)
        self.assertGreaterEqual(len(data["borrowers_without_applications"]), 1)

    def test_all_applications_reference_existing_borrowers(self) -> None:
        if not OUTPUT_FILE.exists():
            self.skipTest("Файл generated_test_data.json ещё не создан.")
        data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        borrower_ids = {b["id"] for b in data["borrowers"]}
        for app in data["applications"]:
            self.assertIn(app["borrower_id"], borrower_ids)
            borrower = next(b for b in data["borrowers"] if b["id"] == app["borrower_id"])
            self.assertEqual(app["income"], borrower["income"])
            self.assertEqual(app["client_name"], borrower["name"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

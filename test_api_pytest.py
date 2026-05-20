"""Pytest-тесты API FastAPI с подменой тяжёлой логики скоринга через pytest-mock."""

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

FAKE_APPROVED = "Одобрено! Кредит на сумму 500000 успешно согласован."
FAKE_REJECTED = "Отказ: ваш доход ниже минимального лимита."
FAKE_DB_ERROR = "Ошибка: сбой обработки заявки"


def test_scoring_returns_mocked_approval(mocker):
    mocker.patch("app.credit_scoring", return_value=FAKE_APPROVED)

    response = client.post(
        "/api/v1/scoring",
        json={"income": 200_000, "loan_amount": 500_000},
    )

    assert response.status_code == 200
    assert response.json() == {"status": FAKE_APPROVED}


def test_scoring_returns_mocked_rejection(mocker):
    mocker.patch("app.credit_scoring", return_value=FAKE_REJECTED)

    response = client.post(
        "/api/v1/scoring",
        json={"income": 50_000, "loan_amount": 100_000},
    )

    assert response.status_code == 200
    assert response.json() == {"status": FAKE_REJECTED}
    assert "Отказ" in response.json()["status"]


def test_scoring_returns_mocked_database_error_status(mocker):
    """Имитация ответа при сбое бизнес-логики / БД без реального подключения."""
    mocker.patch("app.credit_scoring", return_value=FAKE_DB_ERROR)

    response = client.post(
        "/api/v1/scoring",
        json={"income": 180_000, "loan_amount": 300_000},
    )

    assert response.status_code == 200
    assert response.json()["status"] == FAKE_DB_ERROR


def test_scoring_calls_credit_scoring_with_request_body(mocker):
    mock_scoring = mocker.patch(
        "app.credit_scoring",
        return_value=FAKE_APPROVED,
    )

    client.post(
        "/api/v1/scoring",
        json={"income": 250_000, "loan_amount": 400_000},
    )

    mock_scoring.assert_called_once_with(250_000, 400_000)


def test_scoring_does_not_call_real_scoring_when_mocked(mocker):
    mock_scoring = mocker.patch("app.credit_scoring", return_value="Mock decision")

    response = client.post(
        "/api/v1/scoring",
        json={"income": 1, "loan_amount": 1},
    )

    assert response.json() == {"status": "Mock decision"}
    mock_scoring.assert_called_once()
    assert mock_scoring.return_value == "Mock decision"


def test_scoring_invalid_body_returns_422(mocker):
    mock_scoring = mocker.patch("app.credit_scoring")

    response = client.post(
        "/api/v1/scoring",
        json={"income": "not-a-number", "loan_amount": 500_000},
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    mock_scoring.assert_not_called()


def test_scoring_missing_field_returns_422(mocker):
    mock_scoring = mocker.patch("app.credit_scoring")

    response = client.post("/api/v1/scoring", json={"income": 200_000})

    assert response.status_code == 422
    mock_scoring.assert_not_called()

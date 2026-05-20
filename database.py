from main import credit_scoring

loan_applications = [
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


def process_all_applications() -> None:
    for app in loan_applications:
        app["status"] = credit_scoring(app["income"], app["loan_amount"])


def print_all_applications() -> None:
    for app in loan_applications:
        status = app.get("status", "— (не обработано)")
        print(
            f"Заявка №{app['id']}: Клиент {app['client_name']}, "
            f"доход {app['income']}, сумма кредита {app['loan_amount']}. "
            f"Статус: {status}"
        )


if __name__ == "__main__":
    process_all_applications()
    print_all_applications()

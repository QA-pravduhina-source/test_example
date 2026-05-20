from main import credit_scoring, log_database_error

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
        try:
            app_id = app["id"]
            income = app["income"]
            loan_amount = app["loan_amount"]
            app["status"] = credit_scoring(income, loan_amount)
        except KeyError as exc:
            log_database_error(
                f"Ошибка БД: отсутствует обязательное поле заявки id={app.get('id', '?')}",
                exc,
            )
            app["status"] = "Ошибка: некорректные данные заявки"
        except (TypeError, ValueError) as exc:
            log_database_error(
                f"Ошибка БД: неверный тип данных заявки id={app.get('id', '?')}",
                exc,
            )
            app["status"] = "Ошибка: некорректные данные заявки"
        except Exception as exc:
            log_database_error(
                f"Ошибка БД: сбой обработки заявки id={app.get('id', '?')}",
                exc,
            )
            app["status"] = "Ошибка: сбой обработки заявки"


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

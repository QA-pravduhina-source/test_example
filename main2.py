user_name = input("Введите ваше имя: ")
birth_year = input("Введите ваш год рождения: ")

birth_year = int(birth_year)
calculated_age = 2026 - birth_year

print(f"{user_name}, ваш возраст в 2026 году: {calculated_age} лет.")
import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Получение данных пользователей")
def test_get_users_list():
    """Получение списка всех пользователей"""
    with allure.step("Подготовка тестовых данных"):
        # Загрузка переменных окружения
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        # Проверка наличия обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    with allure.step("Формирование заголовков запроса"):
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(str(headers), name="Request Headers", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Формирование URL и отправка GET запроса"):
        url = f"{base_url}/api/v1/users"
        
        curl_command = (
            f"curl -X GET '{url}' "
            f"-H 'accept: */*' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(curl_command, name="CURL команда", attachment_type=allure.attachment_type.TEXT)

        response = requests.get(url, headers=headers)

    with allure.step("Проверка ответа от сервера"):
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        users_data = response.json()

        allure.attach(
            str(users_data),
            name="Список пользователей",
            attachment_type=allure.attachment_type.JSON
        )

        with allure.step("Валидация структуры ответа"):
            assert isinstance(users_data, list), "Ответ должен быть списком пользователей"

            if len(users_data) > 0:
                first_user = users_data[0]
                with allure.step("Проверка структуры первого пользователя в списке"):
                    assert isinstance(first_user, dict), "Каждый пользователь должен быть объектом"
                    assert "id" in first_user, "У пользователя должно быть поле 'id'"
                    assert "fio" in first_user, "У пользователя должно быть поле 'fio'"
                    assert "login" in first_user, "У пользователя должно быть поле 'login'"
                    assert "mail" in first_user, "У пользователя должно быть поле 'mail'"
                    assert "phone" in first_user, "У пользователя должно быть поле 'phone'"
                    assert "role_id" in first_user, "У пользователя должно быть поле 'role_id'"
                    assert "tenant_id" in first_user, "У пользователя должно быть поле 'tenant_id'"
                    assert "is_manager" in first_user, "У пользователя должно быть поле 'is_manager'"

                with allure.step("Дополнительные проверки значений"):
                    assert isinstance(first_user["id"], int), "ID пользователя должен быть числом"
                    assert isinstance(first_user["fio"], str) and len(first_user["fio"]) > 0, "ФИО должно быть непустой строкой"
                    assert "@" in first_user["mail"], "Email должен содержать @"
            else:
                allure.attach(
                    "Список пользователей пуст.",
                    name="Примечание",
                    attachment_type=allure.attachment_type.TEXT
                )
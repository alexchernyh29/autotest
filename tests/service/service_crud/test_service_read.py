import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


@allure.feature("Получение данных биллингового сервиса")
def test_get_billing_service_by_id():
    """Получение данных биллингового сервиса по ID из переменной окружения"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        service_id = os.getenv("SERVICE_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert service_id, "SERVICE_ID не задан в .env"

    with allure.step("Формирование заголовков запроса"):
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(str(headers), name="Request Headers", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Формирование URL запроса"):
        url = f"{base_url}/api/v1/billing/service/{service_id}"
        curl_command = f"curl --location '{url}' --header 'accept: application/json' --header 'tockenid: {token}'"
        allure.attach(curl_command, name="CURL команда", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Отправка GET запроса на {url}"):
        response = requests.get(url, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

            try:
                service_data = response.json()
            except requests.exceptions.JSONDecodeError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(str(service_data), name="Service Data", attachment_type=allure.attachment_type.JSON)

            with allure.step("Проверка структуры ответа"):
                assert isinstance(service_data, dict), "Ответ должен быть словарём"
                assert "id" in service_data, "В ответе отсутствует поле 'id'"
                expected_id = str(service_id)
                actual_id = str(service_data["id"])
                assert actual_id == expected_id, f"ID сервиса не совпадает: ожидалось {expected_id}, получено {actual_id}"
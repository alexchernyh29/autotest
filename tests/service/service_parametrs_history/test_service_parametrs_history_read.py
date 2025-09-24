import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


@allure.feature("Получение истории параметров биллингового сервиса")
def test_get_billing_service_parameters_history_by_id():
    """Получение истории параметров биллингового сервиса по ID из переменной окружения"""
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
        url = f"{base_url}/api/v1/billing/service_parametrs_history/{service_id}"
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
                history_data = response.json()
            except requests.exceptions.JSONDecodeError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(str(history_data), name="Service Parameters History Data", attachment_type=allure.attachment_type.JSON)

            with allure.step("Проверка структуры ответа"):
                assert isinstance(history_data, list), "Ответ должен быть списком записей истории параметров"
                
                if history_data:
                    first_record = history_data[0]
                    assert isinstance(first_record, dict), "Каждая запись истории должна быть словарём"
                    required_fields = {"id", "service_id", "parameter_name", "old_value", "new_value", "changed_at"}
                    record_keys = set(first_record.keys())
                    assert required_fields & record_keys, \
                        f"Запись истории должна содержать хотя бы одно из ключевых полей: {required_fields}"
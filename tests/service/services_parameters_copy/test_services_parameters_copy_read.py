# Возвращает список параметров сервиса для указанного service_id /api/v1/billing/services_parametrs?by_service_id={id}
import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Получение параметров биллингового сервиса")
def test_get_billing_services_parameters_by_service_id():
    """Получение параметров сервиса по service_id из переменной окружения"""
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

    with allure.step("Формирование URL с query-параметром"):
        url = f"{base_url}/api/v1/billing/services_parametrs"
        params = {"by_service_id": service_id}

        curl_command = (
            f"curl --location '{url}?by_service_id={service_id}' "
            f"--header 'accept: application/json' "
            f"--header 'tockenid: {token}'"
        )
        allure.attach(curl_command, name="CURL команда", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Отправка GET запроса на {url}"):
        response = requests.get(url, headers=headers, params=params)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

            try:
                parameters_data = response.json()
            except requests.exceptions.JSONDecodeError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(str(parameters_data), name="Service Parameters Data", attachment_type=allure.attachment_type.JSON)

            with allure.step("Проверка структуры ответа"):
                assert isinstance(parameters_data, list), "Ответ должен быть списком параметров"

                if parameters_data:
                    first_param = parameters_data[0]
                    assert isinstance(first_param, dict), "Каждый параметр должен быть словарём"
                    expected_fields = {"id", "service_id", "name", "value", "created_at"}
                    assert set(first_param.keys()) & expected_fields, \
                        f"Параметр должен содержать хотя бы одно из полей: {expected_fields}"
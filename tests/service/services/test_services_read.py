import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

load_dotenv(ENV_FILE)

ORGANIZATION_ID = os.getenv("ORGANIZATION_ID")
SERVICE_SYSTEM_NAME = os.getenv("SERVICE_SYSTEM_NAME")
RENDER_RESOURCE_ID = os.getenv("RENDER_RESOURCE_ID")

assert ORGANIZATION_ID, "ORGANIZATION_ID не задан в .env"
assert SERVICE_SYSTEM_NAME, "SERVICE_SYSTEM_NAME не задан в .env"
assert RENDER_RESOURCE_ID, "RENDER_RESOURCE_ID не задан в .env"

PARAMS_FOR_TEST = [
    ("by_organization_id", ORGANIZATION_ID, "по ID организации"),
    ("by_service_system_name", SERVICE_SYSTEM_NAME, "по системному имени сервиса"),
    ("by_render_resource", RENDER_RESOURCE_ID, "по ID рендер-ресурса"),
]

@allure.feature("Получение списка биллинговых сервисов")
@pytest.mark.parametrize("param_name,param_value,param_description", PARAMS_FOR_TEST)
def test_get_billing_services_by_single_query_param(param_name, param_value, param_description):
    """Тест получения списка сервисов с фильтрацией по одному query-параметру"""
    with allure.step("Подготовка тестовых данных"):
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert param_value, f"Значение для {param_name} не задано в .env"

    with allure.step("Формирование заголовков запроса"):
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(str(headers), name="Request Headers", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Формирование URL с параметром {param_name}={param_value}"):
        url = f"{base_url}/api/v1/billing/services"
        params = {param_name: param_value}

        curl_command = (
            f"curl --location '{url}?{param_name}={param_value}' "
            f"--header 'accept: application/json' "
            f"--header 'tockenid: {token}'"
        )
        allure.attach(curl_command, name="CURL команда", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Отправка GET запроса с фильтрацией {param_description}"):
        response = requests.get(url, headers=headers, params=params)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

            try:
                services_data = response.json()
            except requests.exceptions.JSONDecodeError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(str(services_data), name="Services Data", attachment_type=allure.attachment_type.JSON)

            with allure.step("Проверка структуры ответа"):
                assert isinstance(services_data, list), "Ответ должен быть списком сервисов"
                assert len(services_data) > 0, "Список сервисов не должен быть пустым"
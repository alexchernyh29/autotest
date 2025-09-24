# Копирует параметры из одного сервиса в другой. /api/v1/billing/services_parameters_copy/{id}
import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


@allure.feature("Копирование параметров биллингового сервиса")
def test_copy_billing_service_parameters():
    """Копирование параметров сервиса с указанием целевого service_copy_id"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        service_id = os.getenv("SERVICE_ID")
        service_copy_id = os.getenv("SERVICE_COPY_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert service_id, "SERVICE_ID не задан в .env"
        if service_copy_id is None:
            service_copy_id = "0" 

    with allure.step("Формирование тела запроса и заголовков"):
        payload = {
            "service_copy_id": int(service_copy_id)
        }
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "tockenid": token
        }

        allure.attach(str(headers), name="Request Headers", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(payload), name="Request Body", attachment_type=allure.attachment_type.JSON)

    with allure.step("Формирование URL запроса"):
        url = f"{base_url}/api/v1/billing/services_parameters_copy/{service_id}"
        curl_command = (
            f"curl --location '{url}' \\\n"
            f"  --header 'accept: */*' \\\n"
            f"  --header 'Content-Type: application/json' \\\n"
            f"  --header 'tockenid: {token}' \\\n"
            f"  --data '{str(payload).replace('\'', '\"')}'"
        )
        allure.attach(curl_command, name="CURL команда", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Отправка POST запроса на {url}"):
        response = requests.post(url, headers=headers, json=payload)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code in (200, 201, 204), \
                f"Ожидался успешный статус (200/201/204), получен {response.status_code}"

            if response.status_code != 204 and response.content:
                try:
                    response_data = response.json()
                    allure.attach(str(response_data), name="Response JSON", attachment_type=allure.attachment_type.JSON)
                except requests.exceptions.JSONDecodeError:
                    pass
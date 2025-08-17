# Создает новый тариф на основе предоставленных данных /api/v1/tariff
# tests/test_create_tariff.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, set_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Создание тарифа")
def test_create_tariff():
    """Создание нового тарифа и сохранение его ID в .env"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    url = f"{base_url}/api/v1/tariff"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "tockenid": token
    }

    # Тело запроса
    payload = {
        "name": "AutoTest Tariff",
        "description": "Created by API test",
        "service_id": 1,
        "status_id": 1,
        "type_level_resource": 1,
        "location_id": 1,
        "time_interval_id": 1,
        "permanent_service": 0
    }

    with allure.step("Формирование и отправка POST-запроса"):
        curl_command = (
            f"curl -X POST '{url}' "
            f"-H 'accept: application/json' "
            f"-H 'Content-Type: application/json' "
            f"-H 'tockenid: {token}' "
            f"-d '{str(payload).replace(' ', '').replace("'", '"')}'"
        )
        allure.attach(
            curl_command,
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            str(payload),
            name="Request Body",
            attachment_type=allure.attachment_type.JSON
        )

        response = requests.post(url, json=payload, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200 or response.status_code == 201, \
                f"Ожидался статус 200 или 201, но получен {response.status_code}"

            try:
                response_json = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            assert "id" in response_json, "В ответе отсутствует поле 'id'"
            created_tariff_id = response_json["id"]

            allure.attach(
                str(response_json),
                name="Created Tariff Data",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step(f"Сохранение CREATED_TARIFF_ID={created_tariff_id} в .env"):
                set_key(ENV_FILE, "CREATED_TARIFF_ID", str(created_tariff_id))
                allure.attach(
                    f"CREATED_TARIFF_ID={created_tariff_id}",
                    name="Сохранённый ID тарифа",
                    attachment_type=allure.attachment_type.TEXT
                )

            # Дополнительно проверим, что ID — целое число
            assert isinstance(created_tariff_id, int), "ID тарифа должен быть целым числом"
# Связывает указанный тариф с указанным арендатором /api/v1/tariff_link_tenant
# tests/test_create_tariff_link_tenant.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, set_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Создание связи тарифа с арендатором")
def test_create_tariff_link_tenant():
    """Создание новой связи между тарифом и арендатором (tenant)"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_id = os.getenv("CREATED_TARIFF_ID")
        tenant_id = os.getenv("CREATED_TENANT_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_id, "CREATED_TARIFF_ID не задан в .env"
        assert tenant_id, "CREATED_TENANT_ID не задан в .env"

        try:
            tariff_id = int(tariff_id)
            tenant_id = int(tenant_id)
        except ValueError:
            pytest.fail("CREATED_TARIFF_ID и CREATED_TENANT_ID должны быть числами")

    url = f"{base_url}/api/v1/tariff_link_tenant"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "tockenid": token
    }

    # Тело запроса
    payload = {
        "tariff_id": tariff_id,
        "tenant_id": tenant_id
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
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            payload,
            name="Request Body (JSON)",
            attachment_type=allure.attachment_type.JSON
        )

        response = requests.post(url, json=payload, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code in [200, 201], \
                f"Ожидался статус 200 или 201, но получен {response.status_code}"

            try:
                response_json = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                response_json,
                name="Created Link Data",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(response_json, dict), "Ответ должен быть объектом"
                assert "id" in response_json, "В ответе отсутствует поле 'id'"
                assert response_json["tariff_id"] == tariff_id, "tariff_id не совпадает"
                assert response_json["tenant_id"] == tenant_id, "tenant_id не совпадает"

            created_link_id = response_json["id"]
            with allure.step(f"Сохранение CREATED_LINK_TENANT_ID={created_link_id} в .env"):
                set_key(ENV_FILE, "CREATED_LINK_TENANT_ID", str(created_link_id))
                allure.attach(
                    f"CREATED_LINK_TENANT_ID={created_link_id}",
                    name="ID созданной связи",
                    attachment_type=allure.attachment_type.TEXT
                )
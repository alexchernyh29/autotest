# Создает новую запись настроек тарифа для конкретного арендатора и организации /api/v1/tariff_tenant_settings
# tests/test_create_tariff_tenant_settings.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, set_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Создание настроек арендатора")
def test_create_tariff_tenant_settings():
    """Создание новых настроек арендатора"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_setting_id = os.getenv("CREATED_TARIFF_SETTING_ID")  # Предполагаем, что есть общая настройка
        tariff_link_org_id = os.getenv("CREATED_LINK_ID")           # Связь тарифа с организацией

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_setting_id, "CREATED_TARIFF_SETTING_ID не задан в .env"
        assert tariff_link_org_id, "CREATED_LINK_ID не задан в .env"

        try:
            tariff_setting_id = int(tariff_setting_id)
            tariff_link_org_id = int(tariff_link_org_id)
        except ValueError:
            pytest.fail("CREATED_TARIFF_SETTING_ID и CREATED_LINK_ID должны быть числами")

    url = f"{base_url}/api/v1/tariff_tenant_settings"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "tockenid": token
    }

    # Тело запроса
    payload = {
        "tariff_setting_id": tariff_setting_id,
        "tariff_link_organization_id": tariff_link_org_id,
        "tenant_rate_price_active": 100,
        "tenant_rate_price_passive": 50
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
                name="Created Tenant Settings",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(response_json, dict), "Ответ должен быть объектом"
                assert "id" in response_json, "В ответе отсутствует поле 'id'"
                assert response_json["tariff_setting_id"] == tariff_setting_id, "tariff_setting_id не совпадает"
                assert response_json["tariff_link_organization_id"] == tariff_link_org_id, "Связь не совпадает"
                assert response_json["tenant_rate_price_active"] == payload["tenant_rate_price_active"], "active цена не совпадает"
                assert response_json["tenant_rate_price_passive"] == payload["tenant_rate_price_passive"], "passive цена не совпадает"

            created_setting_id = response_json["id"]
            with allure.step(f"Сохранение CREATED_TENANT_SETTING_ID={created_setting_id} в .env"):
                set_key(ENV_FILE, "CREATED_TENANT_SETTING_ID", str(created_setting_id))
                allure.attach(
                    f"CREATED_TENANT_SETTING_ID={created_setting_id}",
                    name="ID созданной настройки арендатора",
                    attachment_type=allure.attachment_type.TEXT
                )
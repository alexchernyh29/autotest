# Возвращает настройки тарифа для арендатора по указанному ID /api/v1/tariff_tenant_settings/{id}
# tests/test_get_tariff_tenant_settings_by_id.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Получение настроек арендатора по ID")
def test_get_tariff_tenant_settings_by_id():
    """Получение информации о настройках арендатора по ID"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        setting_id = os.getenv("CREATED_TENANT_SETTING_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert setting_id, "CREATED_TENANT_SETTING_ID не задан в .env. Сначала создайте настройку."

        try:
            setting_id = int(setting_id)
        except ValueError:
            pytest.fail("CREATED_TENANT_SETTING_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff_tenant_settings/{setting_id}"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step(f"Отправка GET-запроса на {url}"):
        curl_command = (
            f"curl -X GET '{url}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
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

        response = requests.get(url, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Ожидался статус 200, но получен {response.status_code}"

            try:
                setting_data = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                setting_data,
                name="Tariff Tenant Settings Data",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(setting_data, dict), "Ожидался объект (dict)"
                assert "id" in setting_data, "В ответе отсутствует поле 'id'"
                assert "tariff_setting_id" in setting_data, "Отсутствует 'tariff_setting_id'"
                assert "tariff_link_organization_id" in setting_data, "Отсутствует 'tariff_link_organization_id'"
                assert "tenant_rate_price_active" in setting_data, "Отсутствует 'tenant_rate_price_active'"
                assert "tenant_rate_price_passive" in setting_data, "Отсутствует 'tenant_rate_price_passive'"

                # Проверка соответствия ID
                assert setting_data["id"] == setting_id, \
                    f"Ожидалась настройка с ID={setting_id}, но получен ID={setting_data.get('id')}"
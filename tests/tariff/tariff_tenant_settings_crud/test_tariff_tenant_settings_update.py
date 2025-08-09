# Обновляет настройки тарифа для указанного арендатора /api/v1/tariff_tenant_settings/{id}4
# tests/test_update_tariff_tenant_settings.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Обновление настроек арендатора")
def test_update_tariff_tenant_settings():
    """Обновление настроек арендатора по ID из .env"""
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
        "accept": "*/*",
        "Content-Type": "application/json",
        "tockenid": token
    }

    # Обновлённые данные
    payload = {
        "tariff_setting_id": 1,  # Пример: обновляем на другую настройку
        "tariff_link_organization_id": 1,
        "tenant_rate_price_active": 200,
        "tenant_rate_price_passive": 100
    }

    with allure.step(f"Отправка PUT-запроса на {url} для обновления настроек арендатора"):
        curl_command = (
            f"curl -X PUT '{url}' "
            f"-H 'accept: */*' "
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

        response = requests.put(url, json=payload, headers=headers)

        with allure.step("Проверка ответа на обновление"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Ожидался статус 200, но получен {response.status_code}"

            try:
                updated_data = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                updated_data,
                name="Updated Tenant Settings",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка, что данные обновились корректно"):
                assert updated_data.get("id") == setting_id, "ID не совпадает"
                assert updated_data.get("tariff_setting_id") == payload["tariff_setting_id"], "tariff_setting_id не обновился"
                assert updated_data.get("tariff_link_organization_id") == payload["tariff_link_organization_id"], "Связь не обновилась"
                assert updated_data.get("tenant_rate_price_active") == payload["tenant_rate_price_active"], "active цена не обновилась"
                assert updated_data.get("tenant_rate_price_passive") == payload["tenant_rate_price_passive"], "passive цена не обновилась"

    # Дополнительная проверка: GET-запрос для подтверждения изменений
    with allure.step("Подтверждение: GET-запрос после обновления"):
        get_response = requests.get(url, headers={"accept": "application/json", "tockenid": token})
        assert get_response.status_code == 200, "GET после обновления вернул не 200"

        actual_data = get_response.json()
        assert actual_data.get("tenant_rate_price_active") == payload["tenant_rate_price_active"], "active цена не сохранилась"
        assert actual_data.get("tenant_rate_price_passive") == payload["tenant_rate_price_passive"], "passive цена не сохранилась"
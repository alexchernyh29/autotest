# Удаляет настройки тарифа для указанного арендатора по ID /api/v1/tariff_tenant_settings/{id}
# tests/test_delete_tariff_tenant_settings.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, unset_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Удаление настроек арендатора")
def test_delete_tariff_tenant_settings():
    """Удаление настроек арендатора по ID из .env"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        setting_id = os.getenv("CREATED_TENANT_SETTING_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert setting_id, "CREATED_TENANT_SETTING_ID не задан в .env. Нечего удалять."

        try:
            setting_id = int(setting_id)
        except ValueError:
            pytest.fail("CREATED_TENANT_SETTING_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff_tenant_settings/{setting_id}"
    headers = {
        "accept": "*/*",
        "tockenid": token
    }

    with allure.step(f"Отправка DELETE-запроса на {url}"):
        curl_command = (
            f"curl -X DELETE '{url}' "
            f"-H 'accept: */*' "
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

        response = requests.delete(url, headers=headers)

        with allure.step("Проверка ответа на удаление"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            # API может возвращать 200 (OK) или 204 (No Content)
            assert response.status_code in [200, 204], \
                f"Ожидался статус 200 или 204, но получен {response.status_code}"

            if response.text.strip():
                try:
                    delete_response = response.json()
                    allure.attach(
                        delete_response,
                        name="Delete Response",
                        attachment_type=allure.attachment_type.JSON
                    )
                except ValueError:
                    pass  # Пустой ответ — норма при 204

    # Проверка, что сущность действительно удалена
    with allure.step("Подтверждение удаления: GET должен вернуть 404"):
        get_response = requests.get(
            f"{base_url}/api/v1/tariff_tenant_settings/{setting_id}",
            headers={"accept": "application/json", "tockenid": token}
        )
        assert get_response.status_code == 404, \
            f"Ожидался статус 404 после удаления, но получен {get_response.status_code}"

        allure.attach(
            f"Настройка арендатора с ID={setting_id} больше не существует — подтверждено 404",
            name="Результат проверки",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Очистка: удаление CREATED_TENANT_SETTING_ID из .env"):
        unset_key(ENV_FILE, "CREATED_TENANT_SETTING_ID")
        allure.attach(
            "Переменная CREATED_TENANT_SETTING_ID удалена из .env",
            name="Очистка окружения",
            attachment_type=allure.attachment_type.TEXT
        )
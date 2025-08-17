# Удаляет указанную связь между тарифом и арендатором /api/v1/tariff_link_tenant/{tariff_link_tenant_id}
# tests/test_delete_tariff_link_tenant.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, unset_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Удаление связи тарифа с арендатором")
def test_delete_tariff_link_tenant():
    """Удаление связи между тарифом и арендатором по ID из .env"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        link_id = os.getenv("CREATED_LINK_TENANT_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert link_id, "CREATED_LINK_TENANT_ID не задан в .env. Нечего удалять."

        try:
            link_id = int(link_id)
        except ValueError:
            pytest.fail("CREATED_LINK_TENANT_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff_link_tenant/{link_id}"
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

            # API может возвращать 200, 204 при успешном удалении
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

    # Проверка, что связь действительно удалена
    with allure.step("Подтверждение удаления: GET должен вернуть 404"):
        get_response = requests.get(
            f"{base_url}/api/v1/tariff_link_tenant/{link_id}",
            headers={"accept": "application/json", "tockenid": token}
        )
        assert get_response.status_code == 404, \
            f"Ожидался статус 404 после удаления, но получен {get_response.status_code}"

        allure.attach(
            f"Связь с ID={link_id} больше не существует — подтверждено 404",
            name="Результат проверки",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Очистка: удаление CREATED_LINK_TENANT_ID из .env"):
        unset_key(ENV_FILE, "CREATED_LINK_TENANT_ID")
        allure.attach(
            "Переменная CREATED_LINK_TENANT_ID удалена из .env",
            name="Очистка окружения",
            attachment_type=allure.attachment_type.TEXT
        )
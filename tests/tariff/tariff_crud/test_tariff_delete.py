# Удаляет тариф /api/v1/tariff/{id}
# tests/test_delete_tariff.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, unset_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Удаление тарифа")
def test_delete_tariff():
    """Удаление тарифа по ID из .env"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_id = os.getenv("CREATED_TARIFF_ID")

        # Проверяем обязательные переменные
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_id, "CREATED_TARIFF_ID не задан в .env. Нечего удалять."

        try:
            tariff_id = int(tariff_id)
        except ValueError:
            pytest.fail("CREATED_TARIFF_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff/{tariff_id}"
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

            # Ожидаем 200, 204 или 201 — в зависимости от API
            assert response.status_code in [200, 204, 201], \
                f"Ожидался статус 200, 204 или 201, но получен {response.status_code}"

            if response.text:
                try:
                    delete_response = response.json()
                    allure.attach(
                        delete_response,
                        name="Delete Response",
                        attachment_type=allure.attachment_type.JSON
                    )
                except ValueError:
                    pass  # Некоторые API возвращают пустой ответ при 204

    # Дополнительная проверка: GET после удаления должен вернуть 404
    with allure.step("Проверка, что тариф действительно удалён (GET должен вернуть 404)"):
        get_response = requests.get(
            f"{base_url}/api/v1/tariff/{tariff_id}",
            headers={"accept": "*/*", "tockenid": token}
        )
        assert get_response.status_code == 404, \
            f"Ожидался статус 404 после удаления, но получен {get_response.status_code}"

        allure.attach(
            "Тариф больше не доступен — подтверждено 404",
            name="Подтверждение удаления",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Очистка: удаление CREATED_TARIFF_ID из .env"):
        unset_key(ENV_FILE, "CREATED_TARIFF_ID")
        allure.attach(
            "Переменная CREATED_TARIFF_ID удалена из .env",
            name="Очистка окружения",
            attachment_type=allure.attachment_type.TEXT
        )
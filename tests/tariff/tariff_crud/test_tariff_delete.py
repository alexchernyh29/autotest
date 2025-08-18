# Удаляет тариф /api/v1/tariff/{id}
# tests/tariff/tariff_crud/test_tariff_delete.py

import os
import json  # Добавлен
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, unset_key
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


@allure.feature("Тарифы")
@allure.story("Удаление тарифа")
def test_delete_tariff():
    """
    Тест удаления тарифа по ID.
    Проверяет:
    1. Статус-код 200
    2. Тело ответа — null или пустое
    3. GET после удаления возвращает 404
    4. Очистка переменной из .env
    """
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_id = os.getenv("CREATED_TARIFF_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_id, "CREATED_TARIFF_ID не задан в .env. Нечего удалять."

        try:
            tariff_id = int(tariff_id)
            assert tariff_id > 0, "CREATED_TARIFF_ID должен быть положительным числом"
        except (ValueError, TypeError):
            pytest.fail("CREATED_TARIFF_ID должен быть целым положительным числом")

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
        allure.attach(curl_command, name="CURL команда", attachment_type=AttachmentType.TEXT)
        allure.attach(
            json.dumps(headers, indent=2, ensure_ascii=False),
            name="Request Headers",
            attachment_type=AttachmentType.JSON
        )

        response = requests.delete(url, headers=headers)

        with allure.step("Проверка ответа от DELETE"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse Body: {response.text}",
                name="Response Details",
                attachment_type=AttachmentType.TEXT
            )

            # Проверка статуса
            assert response.status_code == 200, (
                f"Ожидался статус 200, но получен {response.status_code}. "
                f"Тело ответа: {response.text}"
            )

            # Проверка тела: null или пустое
            response_text = response.text.strip()

            if not response_text:
                allure.attach(
                    "Тело ответа пустое (ожидаемо)",
                    name="Body Check",
                    attachment_type=AttachmentType.TEXT
                )
            else:
                try:
                    delete_response = response.json()
                    # ✅ Исправлено: используем json.dumps для None/dict
                    allure.attach(
                        json.dumps(delete_response, indent=2, ensure_ascii=False),
                        name="Delete Response (JSON)",
                        attachment_type=AttachmentType.JSON
                    )
                    # Проверяем, что ответ — null
                    assert delete_response is None, "Ожидалось, что тело ответа — null"
                except ValueError:
                    pytest.fail(f"Ответ не является валидным JSON и не пустой: {response_text}")

    # === Проверка, что тариф действительно удалён ===
    with allure.step("Подтверждение удаления: GET должен вернуть 404"):
        get_response = requests.get(
            f"{base_url}/api/v1/tariff/{tariff_id}",
            headers={"accept": "*/*", "tockenid": token}
        )

        allure.attach(
            f"GET после DELETE — статус: {get_response.status_code}, тело: {get_response.text}",
            name="GET Verification",
            attachment_type=AttachmentType.TEXT
        )

        assert get_response.status_code == 404, (
            f"Ожидался 404 после удаления, но получен {get_response.status_code}. "
            f"Тело: {get_response.text}"
        )

        allure.attach(
            "Тариф успешно удалён и больше не доступен (404)",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )

    # === Очистка ===
    with allure.step("Очистка: удаление CREATED_TARIFF_ID из .env"):
        unset_key(ENV_FILE, "CREATED_TARIFF_ID")
        allure.attach(
            "Переменная CREATED_TARIFF_ID удалена из .env",
            name="Очистка окружения",
            attachment_type=AttachmentType.TEXT
        )
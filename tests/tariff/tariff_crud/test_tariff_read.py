# Возвращает информацию о тарифе /api/v1/tariff/{id}
# tests/tariff/tariff_crud/test_tariff_read.py

import os
import json  # Добавлен импорт
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


@allure.feature("Тарифы")
@allure.story("Получение тарифа по ID")
def test_get_tariff():
    """Получение тарифа по ID из .env"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_id = os.getenv("CREATED_TARIFF_ID", "304")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_id, "CREATED_TARIFF_ID не задан в .env."

        try:
            tariff_id = int(tariff_id)
        except ValueError:
            pytest.fail("CREATED_TARIFF_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff/{tariff_id}"
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
            attachment_type=AttachmentType.TEXT
        )

        allure.attach(
            json.dumps(headers, indent=2, ensure_ascii=False),
            name="Request Headers",
            attachment_type=AttachmentType.JSON
        )

        response = requests.get(url, headers=headers)

    with allure.step("Проверка ответа"):
        allure.attach(
            f"Status Code: {response.status_code}\nResponse Body: {response.text}",
            name="Response Details",
            attachment_type=AttachmentType.TEXT
        )

        assert response.status_code == 200, (
            f"Ожидался статус 200, но получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

        try:
            tariff_data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        # ✅ Исправлено: преобразуем dict в JSON-строку
        allure.attach(
            json.dumps(tariff_data, indent=2, ensure_ascii=False),
            name="Tariff Data",
            attachment_type=AttachmentType.JSON
        )

        with allure.step("Проверка структуры ответа"):
            assert isinstance(tariff_data, dict), "Ответ должен быть объектом"
            assert "id" in tariff_data, "Отсутствует поле 'id'"
            assert "name" in tariff_data, "Отсутствует поле 'name'"
            assert "service_id" in tariff_data, "Отсутствует поле 'service_id'"
            assert "location" in tariff_data, "Отсутствует вложенный объект 'location'"
            assert "service" in tariff_data, "Отсутствует вложенный объект 'service'"
            assert "time_interval" in tariff_data, "Отсутствует вложенный объект 'time_interval'"

            # Проверка ID
            assert tariff_data["id"] == tariff_id, (
                f"Ожидался ID={tariff_id}, но получен {tariff_data['id']}"
            )

            # Проверка, что имя не пустое
            assert tariff_data["name"].strip(), "Поле 'name' не должно быть пустым"

    with allure.step("✅ Тест успешно пройден"):
        allure.attach(
            f"Успешно получен тариф: ID={tariff_data['id']}, Name='{tariff_data['name']}'",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
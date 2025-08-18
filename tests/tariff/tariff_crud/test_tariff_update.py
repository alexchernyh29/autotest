# Обновляет информацию о тарифе /api/v1/tariff/{id}
# tests/tariff/tariff_crud/test_tariff_update.py

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
@allure.story("Обновление тарифа")
def test_update_tariff():
    """
    Тест обновления тарифа через PUT /api/v1/tariff/{id}
    Проверяет:
    1. Успешный статус 200 при обновлении
    2. Все обновлённые поля через GET-запрос (включая вложенные объекты)
    """
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_id = os.getenv("CREATED_TARIFF_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_id, "CREATED_TARIFF_ID не задан в .env"

        try:
            tariff_id = int(tariff_id)
            assert tariff_id > 0, "CREATED_TARIFF_ID должен быть положительным числом"
        except (ValueError, TypeError):
            pytest.fail("CREATED_TARIFF_ID должен быть целым положительным числом")

    url = f"{base_url}/api/v1/tariff/{tariff_id}"
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
        "tockenid": token
    }

    payload = {
        "name": "Новый AutoTest Tariff",
        "description": "Created by API test",
        "service_id": 418,
        "status_id": 2,
        "type_level_resource": 2,
        "location_id": 125,
        "time_interval_id": 3,
        "permanent_service": 1
    }

    with allure.step(f"Отправка PUT-запроса на обновление тарифа (ID={tariff_id})"):
        curl_command = (
            f"curl -X PUT '{url}' "
            f"-H 'accept: */*' "
            f"-H 'Content-Type: application/json' "
            f"-H 'tockenid: {token}' "
            f"-d '{json.dumps(payload)}'"
        )
        allure.attach(curl_command, name="CURL команда", attachment_type=AttachmentType.TEXT)
        allure.attach(
            json.dumps(headers, indent=2, ensure_ascii=False),
            name="Request Headers",
            attachment_type=AttachmentType.JSON
        )
        allure.attach(
            json.dumps(payload, indent=2, ensure_ascii=False),
            name="Request Body (JSON)",
            attachment_type=AttachmentType.JSON
        )

        response = requests.put(url, json=payload, headers=headers)

        allure.attach(
            f"Status Code: {response.status_code}\nResponse Body: {response.text}",
            name="Response Details",
            attachment_type=AttachmentType.TEXT
        )

        with allure.step("Проверка: статус-код должен быть 200"):
            assert response.status_code == 200, (
                f"Ожидался статус 200, но получен {response.status_code}. "
                f"Тело ответа: {response.text}"
            )

    # === Проверка через GET ===
    with allure.step("Проверка изменений через GET-запрос"):
        get_response = requests.get(url, headers={"accept": "*/*", "tockenid": token})
        allure.attach(
            f"Status: {get_response.status_code}\nBody: {get_response.text}",
            name="GET Response",
            attachment_type=AttachmentType.TEXT
        )

        assert get_response.status_code == 200, "GET-запрос вернул не 200"

        try:
            actual_data = get_response.json()
        except ValueError:
            pytest.fail("GET-ответ не является валидным JSON")

        # ✅ Исправлено: преобразуем dict в JSON-строку
        allure.attach(
            json.dumps(actual_data, ensure_ascii=False, indent=2),
            name="Actual Tariff Data (GET)",
            attachment_type=AttachmentType.JSON
        )

        with allure.step("Проверка соответствия обновлённых данных"):
            # Простые поля (на верхнем уровне)
            assert actual_data.get("name") == payload["name"], "Имя тарифа не сохранилось"
            assert actual_data.get("description") == payload["description"], "Описание не сохранилось"
            assert actual_data.get("status_id") == payload["status_id"], "status_id не сохранился"
            assert actual_data.get("type_level_resource") == payload["type_level_resource"], "type_level_resource не сохранился"
            assert actual_data.get("permanent_service") == payload["permanent_service"], "permanent_service не сохранился"

            # Проверка service_id через вложенный объект
            service = actual_data.get("service")
            assert service is not None, "Отсутствует объект 'service' в ответе"
            assert service.get("id") == payload["service_id"], "service_id не совпадает"

            # Проверка location_id через вложенный объект
            location = actual_data.get("location")
            assert location is not None, "Отсутствует объект 'location' в ответе"
            assert location.get("id") == payload["location_id"], "location_id не совпадает"

            # Проверка time_interval_id через вложенный объект
            time_interval = actual_data.get("time_interval")
            assert time_interval is not None, "Отсутствует объект 'time_interval' в ответе"
            assert time_interval.get("id") == payload["time_interval_id"], "time_interval_id не совпадает"

    with allure.step("Тест успешно завершён"):
        allure.attach(
            f"Тариф с ID={tariff_id} успешно обновлён и проверен.\n"
            f"Все поля соответствуют ожидаемым значениям.",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
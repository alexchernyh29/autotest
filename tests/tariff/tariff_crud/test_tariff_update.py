# Обновляет информацию о тарифе /api/v1/tariff/{id}
# tests/test_update_tariff.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Обновление тарифа")
def test_update_tariff():
    """Обновление информации о тарифе по ID из .env"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_id = os.getenv("CREATED_TARIFF_ID")

        # Проверяем обязательные переменные
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_id, "CREATED_TARIFF_ID не задан в .env. Запустите сначала test_create_tariff.py"

        tariff_id = int(tariff_id)  # Приводим к int для удобства

    url = f"{base_url}/api/v1/tariff/{tariff_id}"
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
        "tockenid": token
    }

    # Тело запроса с обновлёнными данными
    payload = {
        "name": "Новый тариф",
        "description": "Подробное описание тарифа",
        "service_id": 123,
        "status_id": 1,
        "type_level_resource": 1,
        "location_id": 1,
        "time_interval_id": 1,
        "permanent_service": 0
    }

    with allure.step(f"Отправка PUT-запроса на {url} для обновления тарифа"):
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
                name="Updated Tariff Data",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка, что обновлённые данные соответствуют отправленным"):
                assert updated_data.get("id") == tariff_id, "ID тарифа в ответе не совпадает"
                assert updated_data.get("name") == payload["name"], "Имя тарифа не обновилось"
                assert updated_data.get("description") == payload["description"], "Описание не обновилось"
                assert updated_data.get("service_id") == payload["service_id"], "service_id не обновился"
                assert updated_data.get("status_id") == payload["status_id"], "status_id не обновился"
                assert updated_data.get("type_level_resource") == payload["type_level_resource"], "type_level_resource не обновился"
                assert updated_data.get("location_id") == payload["location_id"], "location_id не обновился"
                assert updated_data.get("time_interval_id") == payload["time_interval_id"], "time_interval_id не обновился"
                assert updated_data.get("permanent_service") == payload["permanent_service"], "permanent_service не обновился"

    # Дополнительно: GET-запрос для проверки, что изменения сохранились
    with allure.step("Дополнительная проверка: GET-запрос для подтверждения изменений"):
        get_response = requests.get(url, headers={"accept": "*/*", "tockenid": token})
        assert get_response.status_code == 200, "GET после обновления вернул не 200"

        actual_data = get_response.json()
        assert actual_data.get("name") == payload["name"], "Имя не сохранилось после обновления"
        assert actual_data.get("description") == payload["description"], "Описание не сохранилось"
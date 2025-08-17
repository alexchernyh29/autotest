# tests/test_get_tariffs_filtered.py

import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Фильтрация тарифов")
def test_get_tariffs_filtered():
    """Получение списка тарифов по фильтрам: by_service_id и by_name"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    filters = {
        "by_service_id": 304,
        "by_name": "Услуги ЦОД"
    }

    url = f"{base_url}/api/v1/tariffs"
    params = filters

    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step("Формирование и отправка GET-запроса с фильтрами"):
        curl_command = (
            f"curl -X GET '{url}?by_service_id={filters['by_service_id']}&by_name={filters['by_name']}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(curl_command, "CURL команда", allure.attachment_type.TEXT)

        allure.attach(
            json.dumps(params, ensure_ascii=False, indent=2),
            "Query Parameters",
            allure.attachment_type.JSON
        )

        allure.attach(
            json.dumps(headers, ensure_ascii=False, indent=2),
            "Request Headers",
            allure.attachment_type.JSON
        )

        response = requests.get(url, params=params, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(f"URL с параметрами: {response.url}", "Финальный URL", allure.attachment_type.TEXT)
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                "Response Details",
                allure.attachment_type.TEXT
            )

            assert response.status_code == 200, f"Ожидался 200, но получен {response.status_code}"

            try:
                tariffs_list = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                json.dumps(tariffs_list, ensure_ascii=False, indent=2),
                "Response (tariffs list)",
                allure.attachment_type.JSON
            )

            assert isinstance(tariffs_list, list), "Ожидался массив тарифов"

            if tariffs_list:
                with allure.step(f"Найдено {len(tariffs_list)} тарифов"):
                    for tariff in tariffs_list:
                        assert isinstance(tariff, dict)
                        assert "id" in tariff
                        assert "name" in tariff
                        assert "service_id" in tariff

                        if params.get("by_service_id"):
                            assert tariff["service_id"] == int(params["by_service_id"]), \
                                f"service_id не совпадает: ожидаем {params['by_service_id']}, получено {tariff['service_id']}"

                        if params.get("by_name"):
                            expected = params["by_name"].lower()
                            actual = tariff["name"].lower()
                            assert expected in actual, \
                                f"Имя '{actual}' не содержит '{expected}'"
            else:
                allure.attach(
                    "Тарифы по фильтру не найдены",
                    "Результат",
                    allure.attachment_type.TEXT
                )
# Возвращает список тарифов /api/v1/tariffs?by_service_id=2121&by_name=wedw

# tests/test_get_tariffs_filtered.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Фильтрация тарифов")
def test_get_tariffs_filtered():
    """Получение списка тарифов по фильтрам: by_service_id и by_name"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        # Проверяем обязательные переменные
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    # Параметры фильтрации
    filters = {
        "by_service_id": 2121,
        "by_name": "wedw"
    }

    # Формируем URL с query-параметрами
    url = f"{base_url}/api/v1/tariffs"
    params = filters

    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step("Формирование и отправка GET-запроса с фильтрами"):
        # Генерация cURL
        curl_command = (
            f"curl -X GET '{url}?by_service_id={filters['by_service_id']}&by_name={filters['by_name']}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(
            curl_command,
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            str(params),
            name="Query Parameters",
            attachment_type=allure.attachment_type.JSON
        )

        allure.attach(
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

        # Отправка запроса
        response = requests.get(url, params=params, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"URL с параметрами: {response.url}",
                name="Финальный URL",
                attachment_type=allure.attachment_type.TEXT
            )
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Ожидался статус 200, но получен {response.status_code}"

            try:
                tariffs_list = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                tariffs_list,
                name="Response (tariffs list)",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(tariffs_list, list), "Ожидался массив тарифов (list)"

                with allure.step(f"Найдено {len(tariffs_list)} тарифов по фильтру"):
                    if len(tariffs_list) > 0:
                        for tariff in tariffs_list:
                            assert isinstance(tariff, dict), "Каждый элемент должен быть объектом"
                            assert "id" in tariff, "Тариф должен содержать поле 'id'"
                            assert "name" in tariff, "Тариф должен содержать поле 'name'"
                            assert "service_id" in tariff, "Тариф должен содержать поле 'service_id'"

                            # Проверяем, что фильтр по service_id соблюдён (если передан)
                            if params.get("by_service_id"):
                                assert tariff["service_id"] == int(params["by_service_id"]), \
                                    f"Тариф id={tariff['id']} имеет service_id={tariff['service_id']}, " \
                                    f"ожидался {params['by_service_id']}"

                            # Проверяем частичное совпадение по имени (если by_name задан)
                            if params.get("by_name"):
                                expected_name_part = params["by_name"].lower()
                                actual_name = tariff["name"].lower()
                                assert expected_name_part in actual_name, \
                                    f"Имя тарифа '{actual_name}' не содержит подстроку '{expected_name_part}'"
                    else:
                        allure.attach(
                            "По заданным фильтрам тарифы не найдены",
                            name="Результат фильтрации",
                            attachment_type=allure.attachment_type.TEXT
                        )
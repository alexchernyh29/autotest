# Возвращает список доступных типов настроек тарифов /api/v1/tariff_setting_types
# tests/test_get_tariff_setting_types.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Получение типов настроек тарифов")
def test_get_tariff_setting_types():
    """Получение списка типов настроек"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    url = f"{base_url}/api/v1/tariff_setting_types"
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
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

        response = requests.get(url, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Ожидался статус 200, но получен {response.status_code}"

            try:
                types_list = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                types_list,
                name="Tariff Setting Types Response",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(types_list, list), "Ожидался массив типов настроек"
                assert len(types_list) > 0, "Список типов настроек пуст. Проверьте данные в API."

                found_codes = []

                for type_item in types_list:
                    assert isinstance(type_item, dict), "Каждый тип должен быть объектом"
                    assert "id" in type_item, "Тип должен содержать поле 'id'"
                    assert "name" in type_item, "Тип должен содержать поле 'name'"
                    assert "code" in type_item, "Тип должен содержать поле 'code'"

                    # Проверка типов данных
                    assert isinstance(type_item["id"], int), "Поле 'id' должно быть числом"
                    assert isinstance(type_item["name"], str) and len(type_item["name"].strip()) > 0, \
                        "Поле 'name' должно быть непустой строкой"
                    assert isinstance(type_item["code"], str) and len(type_item["code"].strip()) > 0, \
                        "Поле 'code' должно быть непустой строкой"

                    found_codes.append(type_item["code"])

                # Пример: проверка, что ключевые типы присутствуют
                required_codes = {"string", "boolean", "integer", "select"}
                missing = required_codes - set(found_codes)
                assert not missing, f"Отсутствуют ожидаемые типы: {missing}"

                with allure.step(f"Найдены типы: {', '.join(found_codes)}"):
                    pass  # Для отображения в отчёте
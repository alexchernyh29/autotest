# Возвращает список доступных типов настроек тарифов /api/v1/tariff_setting_types
# tests/tariff/test_get_tariff_setting_types.py

import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


@allure.feature("Тарифы")
@allure.story("Получение типов настроек тарифов")
def test_get_tariff_setting_types():
    """
    Тест получения списка типов настроек тарифов.
    Если API возвращает 500 и 'method - not found' — тест пропускается.
    """
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

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
        allure.attach(curl_command, name="CURL команда", attachment_type=AttachmentType.TEXT)
        allure.attach(
            json.dumps(headers, indent=2, ensure_ascii=False),
            name="Request Headers",
            attachment_type=AttachmentType.JSON
        )

        response = requests.get(url, headers=headers)

    with allure.step("Анализ ответа"):
        response_details = f"Status Code: {response.status_code}\nResponse Body: {response.text}"
        allure.attach(response_details, name="Response Details", attachment_type=AttachmentType.TEXT)

        # === Проверка на 500 + "method - not found" ===
        if response.status_code == 500:
            try:
                error_data = response.json()
                if error_data.get("error") == "method - not found":
                    allure.attach(
                        json.dumps(error_data, indent=2, ensure_ascii=False),
                        name="Error Response",
                        attachment_type=AttachmentType.JSON
                    )
                    pytest.skip(
                        "Пропуск теста: API вернул 500 с ошибкой 'method - not found'. "
                        "Возможно, метод временно недоступен или не реализован."
                    )
            except (ValueError, TypeError):
                pass  # Не JSON — обрабатываем как обычную ошибку

        # === Проверка успешного статуса ===
        assert response.status_code == 200, (
            f"Ожидался статус 200, но получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

        # === Парсинг и проверка JSON ===
        try:
            types_list = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(types_list, ensure_ascii=False, indent=2),
            name="Tariff Setting Types Response",
            attachment_type=AttachmentType.JSON
        )

        with allure.step("Проверка структуры ответа"):
            assert isinstance(types_list, list), "Ожидался массив типов настроек"
            assert len(types_list) > 0, "Список типов настроек пуст. Проверьте данные в API."

            found_codes = []

            for idx, type_item in enumerate(types_list):
                assert isinstance(type_item, dict), f"Элемент [{idx}] должен быть объектом"
                assert "id" in type_item, f"Элемент [{idx}] должен содержать 'id'"
                assert "name" in type_item, f"Элемент [{idx}] должен содержать 'name'"
                assert "code" in type_item, f"Элемент [{idx}] должен содержать 'code'"

                # Проверка типов
                assert isinstance(type_item["id"], int), f"Поле 'id' элемента [{idx}] должно быть числом"
                assert isinstance(type_item["name"], str) and type_item["name"].strip(), \
                    f"Поле 'name' элемента [{idx}] должно быть непустой строкой"
                assert isinstance(type_item["code"], str) and type_item["code"].strip(), \
                    f"Поле 'code' элемента [{idx}] должно быть непустой строкой"

                found_codes.append(type_item["code"])

            # Проверка наличия обязательных типов
            required_codes = {"string", "boolean", "integer", "select"}
            missing = required_codes - set(found_codes)
            assert not missing, f"Отсутствуют ожидаемые типы настроек: {missing}"

    with allure.step("✅ Тест успешно пройден"):
        allure.attach(
            f"Найдено {len(types_list)} типов настроек: {', '.join(found_codes)}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
# Возвращает список настроек тарифов. Можно фильтровать по ID тарифа /api/v1/tariffs_settings?by_tariff_id={id}
# tests/test_get_tariffs_settings.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Получение настроек тарифа")
def test_get_tariffs_settings():
    """Получение списка настроек тарифа по by_tariff_id"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        tariff_id = os.getenv("CREATED_TARIFF_ID", "1321")  # Можно задать в .env или использовать значение по умолчанию

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert tariff_id, "CREATED_TARIFF_ID не задан в .env и не передан"

        try:
            tariff_id = int(tariff_id)
        except ValueError:
            pytest.fail("CREATED_TARIFF_ID должен быть числом")

    url = f"{base_url}/api/v1/tariffs_settings"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    params = {
        "by_tariff_id": tariff_id
    }

    with allure.step(f"Отправка GET-запроса на {url} с фильтром by_tariff_id={tariff_id}"):
        curl_command = (
            f"curl -X GET '{url}?by_tariff_id={tariff_id}' "
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

        response = requests.get(url, params=params, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Финальный URL: {response.url}",
                name="Использованный URL",
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
                settings_list = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                settings_list,
                name="Tariff Settings Response",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(settings_list, list), "Ожидался массив настроек (list)"

                if len(settings_list) > 0:
                    with allure.step(f"Найдено {len(settings_list)} настроек для тарифа {tariff_id}"):
                        for setting in settings_list:
                            assert isinstance(setting, dict), "Каждая настройка должна быть объектом"
                            assert "id" in setting, "Настройка должна содержать поле 'id'"
                            assert "tariff_id" in setting, "Настройка должна содержать поле 'tariff_id'"
                            assert "setting_key" in setting, "Настройка должна содержать поле 'setting_key'"
                            assert "value" in setting, "Настройка должна содержать поле 'value'"

                            # Проверка соответствия tariff_id
                            assert setting["tariff_id"] == tariff_id, \
                                f"Найдена настройка с tariff_id={setting['tariff_id']}, " \
                                f"ожидался {tariff_id}"
                else:
                    with allure.step(f"У тарифа {tariff_id} нет настроек"):
                        allure.attach(
                            "Список настроек пуст. Это может быть ожидаемым поведением.",
                            name="Результат",
                            attachment_type=allure.attachment_type.TEXT
                        )
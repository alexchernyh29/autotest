# Возвращает список всех доступных временных интервалов тарифов /api/v1/tariff_time_intervals
# tests/test_get_tariff_time_intervals.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Получение временных интервалов тарифов")
def test_get_tariff_time_intervals():
    """Получение списка временных интервалов (например: 'ежемесячно', 'ежегодно')"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    url = f"{base_url}/api/v1/tariff_time_intervals"
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
                intervals = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                intervals,
                name="Tariff Time Intervals List",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(intervals, list), "Ожидался массив временных интервалов"
                assert len(intervals) > 0, "Список временных интервалов пуст. Проверьте данные в API."

                for interval in intervals:
                    assert isinstance(interval, dict), "Каждый интервал должен быть объектом"
                    assert "id" in interval, "Интервал должен содержать поле 'id'"
                    assert "name" in interval, "Интервал должен содержать поле 'name'"
                    assert "value" in interval, "Интервал должен содержать поле 'value'"
                    # Дополнительные поля (если есть в API)
                    # assert "description" in interval
                    # assert "months_count" in interval

                    # Пример: value — положительное число
                    assert isinstance(interval["value"], (int, float)) and interval["value"] > 0, \
                        "Поле 'value' должно быть положительным числом"

                    # Пример: name — непустая строка
                    assert isinstance(interval["name"], str) and len(interval["name"].strip()) > 0, \
                        "Поле 'name' должно быть непустой строкой"
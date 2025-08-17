# tests/resource/category_types/test_get_category_types.py

import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


def get_auth_token(login, password, timeoutlive, domain):
    """
    Получение токена аутентификации
    """
    base_url = os.getenv("API_URL")
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {"accept": "application/json"}

    with allure.step("🔐 Получение токена аутентификации"):
        allure.attach(f"URL: {url}", "Request URL", AttachmentType.TEXT)
        allure.attach(json.dumps(headers, indent=2), "Request Headers", AttachmentType.JSON)
        allure.attach(json.dumps(params, indent=2), "Request Params", AttachmentType.JSON)

        response = requests.post(url, headers=headers, params=params)

        allure.attach(str(response.status_code), "Status Code", AttachmentType.TEXT)
        allure.attach(str(response.headers), "Response Headers", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)

        response.raise_for_status()

        try:
            token_data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        tocken_id = token_data.get("tockenID")
        assert tocken_id, "Поле 'tockenID' отсутствует в ответе"

        allure.attach(tocken_id, "✅ Получен tockenID", AttachmentType.TEXT)
        return tocken_id


@allure.story("Получение типов категорий ресурсов")
def test_get_category_types():
    """
    Тест получения списка типов категорий ресурсов
    Проверяет:
    1. Успешный статус-код (200)
    2. Ответ в формате JSON
    3. Наличие ожидаемых полей в каждом элементе
    4. Непустой ответ (если ожидается хотя бы один элемент)
    """
    with allure.step("📁 Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

        # Отладка: какие переменные загружены
        env_data = {
            "API_URL": os.getenv("API_URL"),
            "API_LOGIN": os.getenv("API_LOGIN"),
            "API_DOMAIN": os.getenv("API_DOMAIN")
        }
        allure.attach(
            json.dumps(env_data, indent=2, ensure_ascii=False),
            "Загруженные переменные",
            AttachmentType.JSON
        )

    base_url = os.getenv("API_URL")
    login = os.getenv("API_LOGIN")
    password = os.getenv("API_PASSWORD")
    domain = os.getenv("API_DOMAIN")

    with allure.step("✅ Проверка обязательных переменных"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    with allure.step("🔑 Получение токена"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    with allure.step("📡 Формирование запроса"):
        url = f"{base_url}/api/v1/resource/category_types"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }

        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(json.dumps(headers, indent=2), "Request Headers", AttachmentType.JSON)

    with allure.step("📤 Отправка GET-запроса"):
        response = requests.get(url, headers=headers)

        allure.attach(str(response.status_code), "Status Code", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)
        allure.attach(str(dict(response.headers)), "Response Headers", AttachmentType.JSON)

    with allure.step("✅ Проверка статуса"):
        assert response.status_code == 200, (
            f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"
        )

    with allure.step("📄 Парсинг JSON"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            "Parsed Response Data",
            AttachmentType.JSON
        )

        assert isinstance(data, list), "Ожидался массив объектов"

    if len(data) == 0:
        with allure.step("⚠️ Список пуст"):
            allure.attach(
                "API вернул пустой список типов категорий.",
                "Предупреждение",
                AttachmentType.TEXT
            )
    else:
        with allure.step(f"🔍 Проверка {len(data)} элементов"):
            required_fields = ["id", "name"]  # ❌ Нет поля 'code' в API

            for idx, item in enumerate(data):
                with allure.step(f"Тип категории #{idx + 1} (ID={item.get('id')})"):
                    assert isinstance(item, dict), "Элемент должен быть объектом"

                    missing = [field for field in required_fields if field not in item]
                    assert not missing, f"Отсутствуют поля: {', '.join(missing)}"

                    # Проверка типов
                    assert isinstance(item["id"], int) and item["id"] > 0, "id должно быть положительным числом"
                    assert isinstance(item["name"], str) and item["name"].strip(), "name должно быть непустой строкой"

        with allure.step("✅ Все проверки пройдены"):
            allure.attach(
                f"Успешно получено {len(data)} типов категорий.",
                "Результат",
                AttachmentType.TEXT
            )
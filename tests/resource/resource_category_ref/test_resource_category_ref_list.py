# tests/resource/category/test_get_resource_categories_list.py

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
            pytest.fail("Ответ на запрос токена не является валидным JSON")

        tocken_id = token_data.get("tockenID")
        assert tocken_id, "Поле 'tockenID' отсутствует в ответе"

        allure.attach(tocken_id, "✅ Получен tockenID", AttachmentType.TEXT)
        return tocken_id


@allure.story("Получение списка всех категорий ресурсов")
def test_get_resource_categories_list():
    """
    Тест: получение списка всех категорий ресурсов
    Эндпоинт: GET /api/v1/resource_categoryes_ref
    Проверяет:
      - статус 200
      - ответ в формате JSON
      - наличие массива данных
      - структуру каждого элемента
      - обязательные поля и типы
    """
    with allure.step("📁 Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

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
        url = f"{base_url}/api/v1/resource_categoryes_ref"
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

        assert isinstance(data, list), "Ожидался массив категорий"

    if len(data) == 0:
        with allure.step("⚠️ Список категорий пуст"):
            allure.attach(
                "API вернул пустой список. Проверьте, есть ли активные категории в системе.",
                "Предупреждение",
                AttachmentType.TEXT
            )
    else:
        with allure.step(f"🔍 Проверка {len(data)} категорий"):
            for idx, category in enumerate(data):
                with allure.step(f"Категория #{idx + 1} (ID={category.get('id')})"):
                    assert isinstance(category, dict), "Каждая категория должна быть объектом"

                    # Обязательные поля верхнего уровня
                    required_fields = ["id", "name", "unitMeasure", "typeRef", "category_type"]
                    missing = [field for field in required_fields if field not in category]
                    assert not missing, f"Отсутствуют поля: {', '.join(missing)}"

                    # Проверка id и name
                    assert isinstance(category["id"], int) and category["id"] > 0, "id должно быть положительным числом"
                    assert isinstance(category["name"], str) and category["name"].strip(), "name должно быть непустой строкой"

                    # Проверка unitMeasure
                    unit_measure = category["unitMeasure"]
                    assert isinstance(unit_measure, dict), "unitMeasure должно быть объектом"
                    assert "id" in unit_measure and isinstance(unit_measure["id"], int) and unit_measure["id"] > 0
                    assert "name" in unit_measure and isinstance(unit_measure["name"], str) and unit_measure["name"].strip()

                    # Проверка typeRef
                    type_ref = category["typeRef"]
                    assert isinstance(type_ref, dict), "typeRef должно быть объектом"
                    assert "id" in type_ref and isinstance(type_ref["id"], int) and type_ref["id"] > 0
                    assert "name" in type_ref and isinstance(type_ref["name"], str) and type_ref["name"].strip()

                    # Проверка category_type
                    cat_type = category["category_type"]
                    assert isinstance(cat_type, dict), "category_type должно быть объектом"
                    assert "id" in cat_type and isinstance(cat_type["id"], int) and cat_type["id"] > 0
                    assert "name" in cat_type and isinstance(cat_type["name"], str) and cat_type["name"].strip()

        with allure.step("✅ Все проверки пройдены"):
            allure.attach(
                f"Успешно получено и проверено {len(data)} категорий ресурсов.",
                "Результат",
                AttachmentType.TEXT
            )
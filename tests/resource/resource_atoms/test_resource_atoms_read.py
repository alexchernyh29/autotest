# tests/resource/atoms/test_get_resource_atoms_filtered.py

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


@allure.story("Получение списка атомов ресурсов с фильтрацией")
def test_get_resource_atoms_filtered():
    """
    Тест: получение списка атомов ресурсов с фильтрами:
    - by_pool_id
    - by_category_id
    Проверяет:
      - статус 200
      - ответ в формате JSON
      - наличие массива данных
      - структуру элементов
      - соответствие фильтрам
    """
    with allure.step("📁 Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Фильтры
        by_pool_id = os.getenv("FILTER_BY_POOL_ID", "441")
        by_category_id = os.getenv("FILTER_BY_CATEGORY_ID", "261")

    with allure.step("✅ Проверка обязательных переменных"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert by_pool_id, "FILTER_BY_POOL_ID не задан"
        assert by_category_id, "FILTER_BY_CATEGORY_ID не задан"

        try:
            pool_id = int(by_pool_id)
            category_id = int(by_category_id)
            assert pool_id > 0, "FILTER_BY_POOL_ID должен быть положительным числом"
            assert category_id > 0, "FILTER_BY_CATEGORY_ID должен быть положительным числом"
        except (ValueError, TypeError):
            pytest.fail("FILTER_BY_POOL_ID и FILTER_BY_CATEGORY_ID должны быть целыми положительными числами")

    with allure.step("🔑 Получение токена"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    with allure.step("📡 Формирование параметров запроса"):
        params = {
            "by_pool_id": pool_id,
            "by_category_id": category_id
        }
        url = f"{base_url}/api/v1/resource_atoms"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }

        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(json.dumps(params, indent=2), "Query Parameters", AttachmentType.JSON)
        allure.attach(json.dumps(headers, indent=2), "Request Headers", AttachmentType.JSON)

    with allure.step("📤 Отправка GET-запроса"):
        response = requests.get(url, headers=headers, params=params)

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

        assert isinstance(data, list), "Ожидался массив атомов ресурсов"

    if len(data) == 0:
        with allure.step("⚠️ Список атомов пуст"):
            allure.attach(
                f"Фильтр by_pool_id={pool_id} и by_category_id={category_id} вернул пустой список. "
                "Проверьте, существуют ли атомы, соответствующие этим критериям.",
                "Предупреждение",
                AttachmentType.TEXT
            )
    else:
        with allure.step(f"🔍 Проверка {len(data)} атомов ресурсов"):
            required_fields = ["id", "name", "category", "pool_id", "link_id", "min_count", "max_count", "cost_price_active", "cost_price_passive", "type_use"]

            for idx, atom in enumerate(data):
                with allure.step(f"Атом ресурса #{idx + 1} (ID={atom.get('id')})"):
                    assert isinstance(atom, dict), "Каждый атом должен быть объектом"

                    missing = [field for field in required_fields if field not in atom]
                    assert not missing, f"Отсутствуют поля: {', '.join(missing)}"

                    # Проверка id и name
                    assert isinstance(atom["id"], int) and atom["id"] > 0
                    assert isinstance(atom["name"], str) and atom["name"].strip()

                    # Проверка category
                    category = atom["category"]
                    assert isinstance(category, dict)
                    assert "id" in category and category["id"] == category_id
                    assert "name" in category and isinstance(category["name"], str)
                    assert "unitMeasure" in category
                    assert "typeRef" in category

                    unit_measure = category["unitMeasure"]
                    assert isinstance(unit_measure, dict)
                    assert "id" in unit_measure and isinstance(unit_measure["id"], int)
                    assert "name" in unit_measure and isinstance(unit_measure["name"], str)

                    type_ref = category["typeRef"]
                    assert isinstance(type_ref, dict)
                    assert "id" in type_ref and isinstance(type_ref["id"], int)
                    assert "name" in type_ref and isinstance(type_ref["name"], str)

                    # Проверка pool_id и link_id
                    assert atom["pool_id"] == pool_id, f"pool_id={atom['pool_id']} ≠ фильтру {pool_id}"
                    assert isinstance(atom["link_id"], int) and atom["link_id"] > 0

                    # Проверка min/max count
                    assert isinstance(atom["min_count"], int) and atom["min_count"] >= 0
                    assert isinstance(atom["max_count"], int) and atom["max_count"] > atom["min_count"]

                    # Цены
                    assert isinstance(atom["cost_price_active"], (int, float)) and atom["cost_price_active"] >= 0
                    assert isinstance(atom["cost_price_passive"], (int, float)) and atom["cost_price_passive"] >= 0

                    # type_use — целое число
                    assert isinstance(atom["type_use"], int)

                    # Проверка времени
                    for time_field in ["create_time", "update_time"]:
                        time_obj = atom[time_field]
                        assert isinstance(time_obj, dict)
                        assert "date" in time_obj
                        assert "timezone" in time_obj
                        assert "timezone_type" in time_obj

                    # Пользователи
                    assert isinstance(atom["create_user_id"], int)
                    assert isinstance(atom["update_user_id"], int)

                    # Дополнительные поля
                    assert isinstance(atom["duplicate"], bool)
                    assert isinstance(atom["usedInTS"], int)

        with allure.step("✅ Все проверки пройдены"):
            allure.attach(
                f"Успешно получено и проверено {len(data)} атомов ресурсов с by_pool_id={pool_id} и by_category_id={category_id}.",
                "Результат",
                AttachmentType.TEXT
            )
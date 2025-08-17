import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, find_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType


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
        assert tocken_id, "Поле 'tockenID' отсутствует в ответе при получении токена"

        allure.attach(tocken_id, "✅ Получен tockenID", AttachmentType.TEXT)
        return tocken_id


@allure.story("Получение списка всех местоположений ресурсов")
def test_get_resource_locations():
    """
    Тест: получение списка всех местоположений ресурсов
    Эндпоинт: GET /api/v1/resource_locations
    Проверяет:
      - статус 200
      - ответ в формате JSON
      - наличие массива данных
      - структуру каждого элемента
      - обязательные поля и типы
    """
    with allure.step("📁 Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

        # Отладка: какие переменные загружены
        api_vars = {
            "API_URL": os.getenv("API_URL"),
            "API_LOGIN": os.getenv("API_LOGIN"),
            "API_DOMAIN": os.getenv("API_DOMAIN")
        }
        allure.attach(
            json.dumps(api_vars, indent=2, ensure_ascii=False),
            "Загруженные переменные окружения",
            AttachmentType.JSON
        )

    base_url = os.getenv("API_URL")
    login = os.getenv("API_LOGIN")
    password = os.getenv("API_PASSWORD")
    domain = os.getenv("API_DOMAIN")

    with allure.step("✅ Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    with allure.step("🔑 Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    with allure.step("📡 Формирование запроса"):
        url = f"{base_url}/api/v1/resource_locations"
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

    with allure.step("✅ Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. Ответ: {response.text}"
        )

    with allure.step("📄 Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            "Parsed Response Data",
            AttachmentType.JSON
        )

        assert isinstance(data, list), "Ожидался массив местоположений"

    if len(data) == 0:
        with allure.step("⚠️ Список местоположений пуст"):
            allure.attach(
                "API вернул пустой список. Проверьте, есть ли активные местоположения в системе.",
                "Предупреждение",
                AttachmentType.TEXT
            )
    else:
        with allure.step(f"🔍 Проверка структуры {len(data)} элементов"):
            required_fields = ["id", "name", "address", "create_time", "update_time", "create_user_id", "update_user_id"]

            for idx, location in enumerate(data):
                with allure.step(f"📍 Местоположение #{idx + 1} (ID={location.get('id')})"):
                    assert isinstance(location, dict), "Каждое местоположение должно быть объектом"

                    missing = [field for field in required_fields if field not in location]
                    assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

                    # Проверка типов
                    assert isinstance(location["id"], int) and location["id"] > 0, "id должно быть положительным целым числом"
                    assert isinstance(location["name"], str) and location["name"].strip(), "name должно быть непустой строкой"
                    assert isinstance(location["address"], str) and location["address"].strip(), "address должно быть непустой строкой"
                    assert isinstance(location["create_user_id"], int), "create_user_id должно быть числом"
                    assert isinstance(location["update_user_id"], int), "update_user_id должно быть числом"

                    # Проверка create_time и update_time
                    for time_field in ["create_time", "update_time"]:
                        time_obj = location[time_field]
                        assert isinstance(time_obj, dict), f"{time_field} должно быть объектом"
                        assert "date" in time_obj, f"{time_field}.date отсутствует"
                        assert "timezone" in time_obj, f"{time_field}.timezone отсутствует"
                        assert "timezone_type" in time_obj, f"{time_field}.timezone_type отсутствует"

                        assert isinstance(time_obj["date"], str) and len(time_obj["date"]) >= 19, f"{time_field}.date должно быть строкой формата 'YYYY-MM-DD HH:MM:SS'"
                        assert isinstance(time_obj["timezone"], str) and "/" in time_obj["timezone"], f"{time_field}.timezone должно быть строкой вида 'Region/City'"
                        assert isinstance(time_obj["timezone_type"], int), f"{time_field}.timezone_type должно быть целым числом"

                    # Опционально: проверка, что update_time >= create_time
                    create_date = location["create_time"]["date"]
                    update_date = location["update_time"]["date"]
                    assert update_date >= create_date, f"update_time ({update_date}) < create_time ({create_date})"

        with allure.step("✅ Все проверки пройдены"):
            allure.attach(
                f"Успешно получено и проверено {len(data)} местоположений ресурсов.",
                "Результат",
                AttachmentType.TEXT
            )
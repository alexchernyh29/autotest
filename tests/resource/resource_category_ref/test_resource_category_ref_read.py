# Возвращает информацию о категории ресурса /api/v1/resource_category_ref/{id}
import os
import pytest
import requests
import allure
from dotenv import load_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


def get_auth_token(login, password, timeoutlive, domain):
    """
    Получение токена аутентификации (как в предыдущих тестах)
    """
    base_url = os.getenv("API_URL")
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {
        "accept": "application/json"
    }

    with allure.step("Отправка запроса для получения токена"):
        allure.attach(f"URL: {url}", name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(params), name="Request Params", attachment_type=AttachmentType.TEXT)

        response = requests.post(url, headers=headers, params=params)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    response.raise_for_status()
    token_data = response.json()
    return token_data.get("tockenID")  


@allure.story("Получение информации о категории ресурса по ID")
def test_get_resource_category_by_id():
    """
    Тест: получение данных о категории ресурса по ID
    Эндпоинт: GET /api/v1/resource_category_ref/{id}
    Проверяет:
      - статус 200
      - валидный JSON
      - наличие и корректность всех полей
      - соответствие ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # ID категории для запроса
        category_id = os.getenv("RESOURCE_CATEGORY_ID_TO_GET")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert category_id, "RESOURCE_CATEGORY_ID_TO_GET не задан в .env"

    try:
        category_id = int(category_id)
        assert category_id > 0, "RESOURCE_CATEGORY_ID_TO_GET должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_CATEGORY_ID_TO_GET должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_category_ref/{category_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка GET-запроса для получения категории с ID={category_id}"):
        response = requests.get(url, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Категория с ID={category_id} не найдена. Проверьте корректность ID.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный ID: {category_id}. Ответ: {response.text}")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        # Ожидаемые поля (соответствуют эндпоинту создания)
        required_fields = [
            "id", "name", "type_ref_id", "unit_measure_id", "category_type_id", "created_at"
        ]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка значений
        assert isinstance(data["id"], int) and data["id"] > 0, "ID должно быть положительным целым"
        assert data["id"] == category_id, f"Вернулся ID={data['id']}, ожидался {category_id}"

        assert isinstance(data["name"], str) and len(data["name"]) > 0, "name должно быть непустой строкой"
        assert isinstance(data["type_ref_id"], int) and data["type_ref_id"] > 0, "type_ref_id должно быть положительным"
        assert isinstance(data["unit_measure_id"], int) and data["unit_measure_id"] > 0, "unit_measure_id должно быть положительным"
        assert isinstance(data["category_type_id"], int) and data["category_type_id"] > 0, "category_type_id должно быть положительным"

        assert isinstance(data["created_at"], str), "created_at должно быть строкой"
        assert "T" in data["created_at"] and "Z" in data["created_at"], "created_at должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Успешно получена категория: ID={data['id']}, Name='{data['name']}', "
            f"Type Ref ID={data['type_ref_id']}, Unit Measure ID={data['unit_measure_id']}, "
            f"Category Type ID={data['category_type_id']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
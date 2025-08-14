# Создает новый атом ресурса /api/v1/resource_atom
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


@allure.story("Создание атомарного ресурса (resource_atom)")
def test_create_resource_atom():
    """
    Тест создания нового атомарного ресурса через POST /api/v1/resource_atom
    Проверяет:
    1. Успешный статус-код (201 или 200 — зависит от API)
    2. Валидность ответа (наличие ID, имени и других ожидаемых полей)
    3. Корректность переданных данных в ответе
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса для создания resource_atom"):
        request_body = {
            "category_id": 0,
            "name": "Тестовый ресурс",
            "description": "Описание созданного тестового атомарного ресурса"
        }
        allure.attach(str(request_body), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_atom"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание resource_atom"):
        response = requests.post(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        # Обычно при создании — 201 Created, но может быть и 200
        assert response.status_code in [200, 201], (
            f"Ошибка при создании resource_atom. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        required_fields = ["id", "category_id", "name", "description"]
        missing_fields = [field for field in required_fields if field not in data]

        assert not missing_fields, f"В ответе отсутствуют обязательные поля: {', '.join(missing_fields)}"

        # Проверка, что данные совпадают с отправленными
        assert data["name"] == request_body["name"], "Имя в ответе не совпадает с отправленным"
        assert data["description"] == request_body["description"], "Описание не совпадает"
        assert data["category_id"] == request_body["category_id"], "category_id не совпадает"

    with allure.step("Проверка типа данных полей"):
        assert isinstance(data["id"], int), "Поле 'id' должно быть числом"
        assert data["id"] > 0, "ID должен быть положительным числом"

    with allure.step("Ресурс успешно создан"):
        allure.attach(f"Создан resource_atom с ID: {data['id']}", name="Результат", attachment_type=AttachmentType.TEXT)
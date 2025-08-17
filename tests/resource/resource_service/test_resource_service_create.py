# tests/resource_service/test_create_resource_service.py

import os
import pytest
import requests
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


def set_env_variable(key: str, value: str, env_path: str = ENV_FILE):
    """
    Добавляет или обновляет переменную в .env файле
    """
    env_path = Path(env_path)
    lines = []
    key_found = False

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

    with open(env_path, "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip().startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                key_found = True
            else:
                file.write(line)
        if not key_found:
            file.write(f"{key}={value}\n")


@allure.story("Создание нового сервиса ресурсов (resource_service)")
def test_create_resource_service():
    """
    Тест создания нового сервиса ресурсов через POST /api/v1/resource_service
    Ожидаемый ответ: {"id": 123}
    Сохраняет ID в .env как CREATED_RESOURCE_SERVICE_ID
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

    # Генерация уникальных данных
    import time
    unique_name = f"Тестовый сервис {int(time.time())}"
    unique_system_name = f"test_service_{int(time.time())}"

    with allure.step("Формирование тела запроса"):
        request_body = {
            "name": unique_name,
            "system_name": unique_system_name
        }
        allure.attach(str(request_body), name="Request Body (JSON)", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_service"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание сервиса ресурсов"):
        response = requests.post(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code in [200, 201], (
            f"Ошибка при создании сервиса ресурсов. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        assert "id" in data, "В ответе отсутствует поле 'id'"
        assert isinstance(data["id"], int), "Поле 'id' должно быть целым числом"
        assert data["id"] > 0, "ID должен быть положительным числом"

    created_id = data["id"]

    with allure.step("Сохранение ID в .env файл"):
        set_env_variable("CREATED_RESOURCE_SERVICE_ID", str(created_id))
        allure.attach(
            f"Сохранён ID сервиса: {created_id} → .env переменная CREATED_RESOURCE_SERVICE_ID",
            name="Сохранение ID",
            attachment_type=AttachmentType.TEXT
        )

    with allure.step("✅ Тест завершён успешно"):
        allure.attach(
            f"Создан сервис ресурсов:\n"
            f"  ID: {created_id}\n"
            f"  Name (в запросе): {unique_name}\n"
            f"  System Name (в запросе): {unique_system_name}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
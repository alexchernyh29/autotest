# tests/resource_service/test_get_resource_service_by_id.py

import os
import pytest
import requests
import allure
from dotenv import load_dotenv, find_dotenv
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
    return token_data.get("tockenID")  # Обратите внимание на опечатку: tockenID


@allure.story("Получение информации о сервисе ресурсов по ID")
def test_get_resource_service_by_id():
    """
    Тест получения данных о сервисе ресурсов по его ID
    Проверяет:
    1. Успешный статус-код (200)
    2. Валидность JSON-ответа
    3. Наличие обязательных полей
    4. Соответствие запрошенному ID
    5. Корректность типов данных
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # 🔹 Берём ID из созданного ранее сервиса
        service_id_str = os.getenv("LAST_CREATED_SERVICE_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert service_id_str, (
            "LAST_CREATED_SERVICE_ID не найден в .env. "
            "Сначала выполните тест создания сервиса ресурсов."
        )

    try:
        service_id = int(service_id_str)
        assert service_id > 0, "ID сервиса ресурсов должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("LAST_CREATED_SERVICE_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для получения сервиса ресурсов (ID={service_id})"):
        url = f"{base_url}/api/v1/resource_service/{service_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка GET-запроса"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Сервис ресурсов с ID={service_id} не найден. "
                       "Возможно, он был удалён или не был создан.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный формат ID: {service_id}.")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка API: статус {response.status_code}, тело: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        required_fields = ["id", "name", "system_name"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов
        assert isinstance(data["id"], int), "Поле 'id' должно быть целым числом"
        assert isinstance(data["name"], str), "Поле 'name' должно быть строкой"
        assert isinstance(data["system_name"], str), "Поле 'system_name' должно быть строкой"

        # Проверка соответствия ID
        assert data["id"] == service_id, (
            f"Ожидался ID={service_id}, но получен ID={data['id']}"
        )

        # Проверка, что строки не пустые
        assert data["name"].strip() != "", "Поле 'name' не должно быть пустым"
        assert data["system_name"].strip() != "", "Поле 'system_name' не должно быть пустым"

    with allure.step("✅ Тест завершён успешно"):
        allure.attach(
            f"Успешно получен сервис ресурсов:\n"
            f"  ID: {data['id']}\n"
            f"  Name: {data['name']}\n"
            f"  System Name: {data['system_name']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
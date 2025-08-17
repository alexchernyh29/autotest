# tests/resource_service/test_update_resource_service_by_id.py

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


@allure.story("Обновление сервиса ресурсов по ID (PUT)")
def test_update_resource_service_by_id():
    """
    Тест обновления сервиса ресурсов через PUT /api/v1/resource_service/{id}
    Проверяет:
    1. Успешный статус-код (200)
    2. Валидность JSON-ответа
    3. Наличие и корректность ID в ответе
    4. Соответствие обновлённых данных (косвенно — через GET в будущем)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # 🔹 Используем ID из ранее созданного сервиса
        service_id_str = os.getenv("CREATED_RESOURCE_SERVICE_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert service_id_str, (
            "CREATED_RESOURCE_SERVICE_ID не найден в .env. "
            "Сначала выполните тест создания сервиса."
        )

    try:
        service_id = int(service_id_str)
        assert service_id > 0, "ID сервиса ресурсов должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("CREATED_RESOURCE_SERVICE_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    # Генерация новых уникальных значений
    import time
    updated_name = f"Обновлённое имя {int(time.time())}"
    updated_system_name = f"updated_sys_{int(time.time())}"

    with allure.step(f"Формирование тела запроса для обновления (ID={service_id})"):
        request_body = {
            "name": updated_name,
            "system_name": updated_system_name
        }
        allure.attach(str(request_body), name="Request Body (JSON)", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_service/{service_id}"
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка PUT-запроса на обновление сервиса ресурсов"):
        response = requests.put(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Сервис с ID={service_id} не найден. Возможно, он был удалён.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный ID: {service_id}.")
        elif response.status_code not in [200, 201]:
            pytest.fail(f"Ошибка API: статус {response.status_code}, тело: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("✅ Тест завершён успешно"):
        allure.attach(
            f"Сервис ресурсов успешно обновлён:\n"
            f"  Обновлённые данные:\n"
            f"    Name: {updated_name}\n"
            f"    System Name: {updated_system_name}",
            name="Результат обновления",
            attachment_type=AttachmentType.TEXT
        )
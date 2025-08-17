# test_delete_resource_category_ref.py

import os
import pytest
import requests
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = Path(find_dotenv())
assert ENV_FILE.exists(), "Файл .env не найден в корне проекта"


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

    with allure.step("Получение токена аутентификации"):
        allure.attach(f"URL: {url}", "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)
        allure.attach(str(params), "Request Params", AttachmentType.JSON)

        response = requests.post(url, headers=headers, params=params)
        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


@allure.story("Удаление категории ресурса (resource_category_ref)")
def test_delete_resource_category_ref():
    """
    Тест: удаление категории ресурса по ID
    - Использует RESOURCE_CATEGORY_REF_ID из .env
    - Отправляет DELETE-запрос
    - Проверяет только: статус код == 200 → значит всё ок
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    # Чтение переменных
    base_url = os.getenv("API_URL")
    login = os.getenv("API_LOGIN")
    password = os.getenv("API_PASSWORD")
    domain = os.getenv("API_DOMAIN")
    category_id_str = os.getenv("RESOURCE_CATEGORY_REF_ID")

    # Проверка обязательных переменных
    with allure.step("Проверка переменных окружения"):
        assert base_url, "Не задан API_URL в .env"
        assert login, "Не задан API_LOGIN в .env"
        assert password, "Не задан API_PASSWORD в .env"
        assert domain, "Не задан API_DOMAIN в .env"
        assert category_id_str, "Не задан RESOURCE_CATEGORY_REF_ID в .env"

    try:
        category_id = int(category_id_str)
        assert category_id > 0, "RESOURCE_CATEGORY_REF_ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_CATEGORY_REF_ID должен быть целым положительным числом")

    # Получение токена
    with allure.step("Получение токена"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    # Формирование URL и заголовков
    url = f"{base_url}/api/v1/resource_category_ref/{category_id}"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step(f"Отправка DELETE-запроса для удаления категории с ID={category_id}"):
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

        response = requests.delete(url, headers=headers)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text or "null", "Response Body", AttachmentType.TEXT)

    # ЕДИНСТВЕННАЯ ПРОВЕРКА: статус 200
    with allure.step("Проверка: статус ответа == 200"):
        if response.status_code == 200:
            allure.attach("✅ Статус 200 — удаление прошло успешно", "Результат", AttachmentType.TEXT)
        else:
            pytest.fail(f"Ожидался статус 200, получен {response.status_code}. Тело: {response.text}")
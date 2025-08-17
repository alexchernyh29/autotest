# tests/resource_service/test_delete_resource_service_by_id.py

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
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    response.raise_for_status()
    token_data = response.json()
    return token_data.get("tockenID")  # Обратите внимание на опечатку: tockenID


@allure.story("Удаление сервиса ресурсов по ID (DELETE)")
def test_delete_resource_service_by_id():
    """
    Тест удаления сервиса ресурсов.
    Проверяет только: статус-код == 200.
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # 🔹 Берём ID из созданного сервиса
        service_id_str = os.getenv("CREATED_RESOURCE_SERVICE_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert service_id_str, (
            "CREATED_RESOURCE_SERVICE_ID не найден. "
            "Сначала выполните тест создания сервиса."
        )

    try:
        service_id = int(service_id_str)
        assert service_id > 0, "ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("CREATED_RESOURCE_SERVICE_ID должен быть целым числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    with allure.step(f"Формирование URL для удаления (ID={service_id})"):
        url = f"{base_url}/api/v1/resource_service/{service_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка DELETE-запроса"):
        response = requests.delete(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка: статус-код должен быть 200"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

    with allure.step("✅ Удаление прошло успешно (статус 200)"):
        allure.attach(
            f"Сервис ресурсов с ID={service_id} успешно удалён.",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
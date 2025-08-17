# test_delete_resource_location.py

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

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


@allure.story("Удаление местоположения ресурса по ID")
def test_delete_resource_location():
    """
    Тест: удаление местоположения ресурса
    - Берёт ID из RESOURCE_LOCATION_ID
    - Отправляет DELETE
    - Проверяет только статус 200
    - Игнорирует тело ответа (может быть null)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        location_id_str = os.getenv("RESOURCE_LOCATION_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert location_id_str, "RESOURCE_LOCATION_ID не задан в .env"

    try:
        location_id = int(location_id_str)
        assert location_id > 0, "RESOURCE_LOCATION_ID должен быть положительным целым числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_LOCATION_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для DELETE /resource_location/{location_id}"):
        url = f"{base_url}/api/v1/resource_location/{location_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

    with allure.step("Отправка DELETE-запроса"):
        response = requests.delete(url, headers=headers)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text or "null", "Response Body", AttachmentType.TEXT)

    with allure.step("Проверка: статус-код == 200"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

    with allure.step("Тест успешно пройден: удаление подтверждено статусом 200"):
        allure.attach(
            f"Местоположение с ID={location_id} было удалено (статус 200, ответ: {response.text})",
            "Результат",
            AttachmentType.TEXT
        )
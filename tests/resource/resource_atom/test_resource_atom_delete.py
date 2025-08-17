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
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)

    response.raise_for_status()
    token_data = response.json()
    return token_data.get("tockenID")


@allure.story("Удаление атомарного ресурса по ID (DELETE)")
def test_delete_resource_atom_by_id():
    """
    Тест удаления атомарного ресурса.
    Проверяет только: статус-код == 200
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        resource_atom_id = os.getenv("RESOURCE_ATOM_ID", "339")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert resource_atom_id, "RESOURCE_ATOM_ID не задан"

    try:
        resource_atom_id = int(resource_atom_id)
        assert resource_atom_id > 0, "ID ресурса должно быть положительным целым числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_ATOM_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Отправка DELETE-запроса к /api/v1/resource_atom/{resource_atom_id}"):
        url = f"{base_url}/api/v1/resource_atom/{resource_atom_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

        response = requests.delete(url, headers=headers)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)

    with allure.step("Проверка: статус-код == 200"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получено: {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

    with allure.step("Тест пройден: статус-код 200 получен"):
        allure.attach(f"Успешно удалён resource_atom с ID={resource_atom_id}", "Результат", AttachmentType.TEXT)
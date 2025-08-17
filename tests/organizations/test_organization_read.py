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

@allure.story("Получение информации об организации")
def test_get_organization_by_id():
    """
    Тест получения информации об организации по её ID
    Проверяет:
    1. Успешный статус-код (200)
    2. Наличие обязательных полей в ответе
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Получение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        organization_id = os.getenv("ORGANIZATION_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert organization_id, "ORGANIZATION_ID не задан в .env"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    with allure.step("Формирование запроса для получения информации об организации"):
        url = f"{base_url}/api/v1/organization/{organization_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(f"URL: {url}", name="Organization Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Organization Request Headers", attachment_type=AttachmentType.TEXT)

    with allure.step("Отправка запроса информации об организации"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Organization Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Organization Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Organization Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка статус-кода ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении информации об организации. "
            f"Status: {response.status_code}, Response: {response.text}"
        )

    with allure.step("Парсинг и проверка ответа"):
        data = response.json()
        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        assert isinstance(data, dict), "Ответ должен быть объектом организации"

    with allure.step("Проверка соответствия ID организации"):
        assert data["id"] == int(organization_id), (
            f"ID организации ({data['id']}) "
            f"не соответствует запрошенному ({organization_id})"
        )

    with allure.step("Проверка наличия обязательных полей в ответе"):
        required_fields = [
            "name", "tenant_id", "number_contract", "address",
            "contact_name", "contact_phone", "contact_mail",
            "contract_begin_time", "sub_right_ref", "type_right_ref"
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        assert not missing_fields, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"

    with allure.step("Вывод информации об организации"):
        allure.attach(str(data), name="Organization Details", attachment_type=AttachmentType.JSON)
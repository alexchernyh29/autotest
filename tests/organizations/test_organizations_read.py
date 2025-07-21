import os
import pytest
import requests
import allure
from dotenv import load_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@allure.story("Получение организаций по tenant_id")
def test_get_organizations_by_tenant_id():
    """
    Тест получения списка организаций по tenant_id
    Проверяет:
    1. Успешный статус-код (200)
    2. Наличие обязательных полей в ответе
    3. Соответствие запрошенного tenant_id
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Получение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        test_tenant_id = os.getenv("TEST_TENANT_ID", "123")  # Можно переопределить в .env

        allure.attach(f"API_URL: {base_url}", name="API URL", attachment_type=AttachmentType.TEXT)
        allure.attach(f"TEST_TENANT_ID: {test_tenant_id}", name="Tenant ID", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка обязательных переменных"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    with allure.step("Формирование запроса"):
        url = f"{base_url}/api/v1/organizations"
        params = {"by_tenant_id": test_tenant_id}
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        
        allure.attach(f"URL: {url}", name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(params), name="Request Params", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.TEXT)

    with allure.step("Отправка GET запроса"):
        response = requests.get(url, headers=headers, params=params)
        
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка статус-кода"):
        assert response.status_code == 200, (
            f"Ошибка при получении организаций. "
            f"Status: {response.status_code}, Response: {response.text}"
        )

    with allure.step("Парсинг и валидация ответа"):
        data = response.json()
        allure.attach(str(data), name="Response Data", attachment_type=AttachmentType.JSON)
        
        assert isinstance(data, list), "Ответ должен быть списком организаций"
        allure.attach(f"Найдено организаций: {len(data)}", name="Organizations Count", attachment_type=AttachmentType.TEXT)

        if data:
            org = data[0]
            allure.attach(str(org), name="First Organization Data", attachment_type=AttachmentType.JSON)
            
            required_fields = ["id", "name", "tenant_id"]
            missing_fields = [field for field in required_fields if field not in org]
            
            with allure.step("Проверка обязательных полей"):
                assert not missing_fields, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
                
            with allure.step("Проверка соответствия tenant_id"):
                assert str(org["tenant_id"]) == str(test_tenant_id), (
                    f"tenant_id организации ({org['tenant_id']}) "
                    f"не соответствует запрошенному ({test_tenant_id})"
                )
        else:
            allure.attach("Организации не найдены", name="Empty Response", attachment_type=AttachmentType.TEXT)

def get_auth_token(login, password, timeoutlive, domain):
    """
    Получение токена аутентификации с Allure шагами
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
        allure.attach(f"URL: {url}", name="Token Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Token Request Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(params), name="Token Request Params", attachment_type=AttachmentType.TEXT)
        
        response = requests.post(url, headers=headers, params=params)
        
        allure.attach(str(response.status_code), name="Token Response Status", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Token Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Token Response Body", attachment_type=AttachmentType.TEXT)
        
    response.raise_for_status()
    token_data = response.json()
    return token_data.get("tockenID")
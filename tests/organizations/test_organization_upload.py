import os
import pytest
import requests
import allure
from dotenv import load_dotenv
from pathlib import Path
from faker import Faker

# Инициализация Faker
fake = Faker()

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@allure.feature("Организации")
def test_update_organization():
    """Тест обновления организации"""
    with allure.step("Подготовка тестовых данных"):
        # Загрузка переменных окружения
        load_dotenv(ENV_FILE)

        # Получение параметров из .env
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        organization_id = os.getenv("ORGANIZATION_ID") or "388"  # Используем переданный ID или 388 по умолчанию

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert organization_id, "ORGANIZATION_ID не задан в .env"

    with allure.step("Получение токена авторизации"):
        token_id = get_auth_token(base_url, login, password, 600, domain)
        assert token_id, "Не удалось получить tockenID"

    with allure.step("Подготовка данных для обновления"):
        update_data = {
            "name": "Example Company",
            "number_contract": "1234567890",
            "address": "123 Main St, City, Country",
            "fact_address": "456 Elm St, Town, Country",
            "contact_name": "John Doe",
            "contact_data": "Manager",
            "contact_phone": "+1234567890",
            "contact_mail": "john.doe@example.com",
            "description": "This is an example description."
        }
        
        allure.attach(
            str(update_data),
            name="Данные для обновления организации",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Отправка запроса на обновление организации"):
        url = f"{base_url}/api/v1/organization/{organization_id}"
        
        allure.attach(
            f"curl -X PUT '{url}' "
            f"-H 'accept: application/json' "
            f"-H 'content-type: application/json' "
            f"-H 'tockenid: {token_id}' "
            f"-d '{str(update_data).replace("'", '"')}'",
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = requests.put(
            url,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "tockenid": token_id
            },
            json=update_data
        )
        
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Проверка ответа"):
        assert response.status_code == 200, (
            f"Ошибка при обновлении организации. "
            f"Status: {response.status_code}, Response: {response.text}"
        )

        response_data = response.json()
        allure.attach(
            str(response_data),
            name="Ответ сервера",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Проверка обновленных данных"):
        # Получаем обновленные данные организации для проверки
        response = requests.get(
            url,
            headers={
                "accept": "application/json",
                "tockenid": token_id
            }
        )
        
        assert response.status_code == 200, "Не удалось получить данные организации после обновления"
        
        updated_organization = response.json()
        
        # Проверяем, что данные обновились
        for field, expected_value in update_data.items():
            assert str(updated_organization.get(field)) == str(expected_value), (
                f"Поле {field} не было обновлено. "
                f"Ожидалось: {expected_value}, Получено: {updated_organization.get(field)}"
            )

@allure.step("Получение токена аутентификации")
def get_auth_token(base_url, login, password, timeoutlive, domain):
    """Получение токена аутентификации"""
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {"accept": "application/json"}
    
    allure.attach(
        f"curl -X POST '{url}?login={login}&password=*****&timeoutlive={timeoutlive}&domain={domain}' "
        f"-H 'accept: application/json'",
        name="CURL команда",
        attachment_type=allure.attachment_type.TEXT
    )
    
    response = requests.post(url, headers=headers, params=params)
    allure.attach(
        f"Status Code: {response.status_code}\nResponse: {response.text}",
        name="Response Details",
        attachment_type=allure.attachment_type.TEXT
    )
    
    response.raise_for_status()
    token = response.json().get("tockenID")
    
    if token:
        allure.attach(
            f"Полученный токен (первые 10 символов): {token[:10]}...",
            name="Токен",
            attachment_type=allure.attachment_type.TEXT
        )
    
    return token
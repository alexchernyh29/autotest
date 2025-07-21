import os
import pytest
import requests
from dotenv import load_dotenv, set_key
import random
import string
from pathlib import Path
from config import ENV_FILE
import allure
import json

# Определяем путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

def log_curl(request, response):
    """Генерация cURL команды и логирование запроса/ответа"""
    # Формирование cURL
    command = f"curl -X {request.method} '{request.url}'"
    for name, value in request.headers.items():
        command += f" \\\n  -H '{name}: {value}'"
    if request.body:
        try:
            body = json.dumps(json.loads(request.body), indent=2)
        except:
            body = request.body
        command += f" \\\n  -d '{body}'"
    
    # Логирование в Allure
    with allure.step("Детали запроса"):
        allure.attach(
            f"Request Method: {request.method}\n"
            f"Request URL: {request.url}\n"
            f"Request Headers: {json.dumps(dict(request.headers), indent=2)}\n"
            f"Request Body: {request.body if request.body else 'None'}",
            name="Request Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        allure.attach(
            command,
            name="cURL Command",
            attachment_type=allure.attachment_type.TEXT
        )
    
    with allure.step("Детали ответа"):
        try:
            response_body = json.dumps(response.json(), indent=2)
        except:
            response_body = response.text
        
        allure.attach(
            f"Status Code: {response.status_code}\n"
            f"Response Body: {response_body}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

# Фикстура для создания тестового пользователя
@pytest.fixture
def test_user():
    """Фикстура для создания тестового пользователя"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        
        assert base_url is not None, "API_URL не найден в .env файле"
        assert token is not None, "TOKEN_ID не найден в .env файле"
        
        rand_str = ''.join(random.choices(string.ascii_lowercase, k=5))
        user_data = {
            "fio": f"Test User {rand_str}",
            "login": f"test_{rand_str}",
            "password": "TestPass123",
            "mail": f"test.{rand_str}@example.com",
            "phone": f"79{random.randint(1000000, 9999999)}",
            "role_id": 1,
            "tenant_id": 123,
            "is_manager": 1
        }
        
        allure.attach(
            json.dumps(user_data, indent=2),
            name="User Data",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Создание пользователя"):
        response = requests.post(
            f"{base_url}/api/v1/user",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "tockenid": token
            },
            json=user_data
        )
        
        log_curl(response.request, response)
        assert response.status_code == 200, f"Ошибка создания пользователя: {response.text}"
        
        user_id = response.json()["id"]
        allure.attach(
            f"Создан пользователь с ID: {user_id}",
            name="User ID",
            attachment_type=allure.attachment_type.TEXT
        )
        
        yield user_id

def test_get_user(test_user):
    """GET Получение данных пользователя /api/v1/user/(id)"""
    with allure.step("Подготовка данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        user_id = test_user

    with allure.step("Отправка GET запроса"):
        response = requests.get(
            f"{base_url}/api/v1/user/{user_id}",
            headers={
                "accept": "*/*",
                "tockenid": token
            }
        )
        log_curl(response.request, response)

    with allure.step("Проверка ответа"):
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
        response_data = response.json()
        
        allure.attach(
            f"Ожидаемый ID: {user_id}\nПолученный ID: {response_data.get('id')}",
            name="ID Verification",
            attachment_type=allure.attachment_type.TEXT
        )
        assert response_data["id"] == user_id, "ID пользователя не совпадает"

def test_update_user(test_user):
    """PUT Обновление данных пользователя /api/v1/user/(id)"""
    with allure.step("Подготовка данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        user_id = test_user
        
        update_data = {
            "fio": "Updated Name",
            "login": "updated_login",
            "mail": "updated@example.com",
            "phone": "79123456789",
            "role_id": 1,
            "tenant_id": 123,
            "is_manager": 1
        }
        
        allure.attach(
            json.dumps(update_data, indent=2),
            name="Update Data",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Отправка PUT запроса"):
        response = requests.put(
            f"{base_url}/api/v1/user/{user_id}",
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "tockenid": token
            },
            json=update_data
        )
        log_curl(response.request, response)
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"

    with allure.step("Проверка обновленных данных"):
        get_response = requests.get(
            f"{base_url}/api/v1/user/{user_id}",
            headers={"tockenid": token}
        )
        log_curl(get_response.request, get_response)
        
        updated_user = get_response.json()
        
        allure.attach(
            f"Ожидаемое имя: Updated Name\nПолученное имя: {updated_user.get('fio')}",
            name="Name Verification",
            attachment_type=allure.attachment_type.TEXT
        )
        assert updated_user["fio"] == "Updated Name", "Имя пользователя не обновилось"


def test_delete_user(test_user):
    """DELETE Удаление пользователя /api/v1/user/(id)"""
    with allure.step("Подготовка данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        user_id = test_user

    with allure.step("Отправка DELETE запроса"):
        response = requests.delete(
            f"{base_url}/api/v1/user/{user_id}",
            headers={
                "accept": "*/*",
                "tockenid": token
            }
        )
        log_curl(response.request, response)
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"

    with allure.step("Проверка удаления пользователя"):
        get_response = requests.get(
            f"{base_url}/api/v1/user/{user_id}",
            headers={"tockenid": token}
        )
        log_curl(get_response.request, get_response)
        
        allure.attach(
            f"Ожидаемый статус: 404\nПолученный статус: {get_response.status_code}",
            name="Deletion Verification",
            attachment_type=allure.attachment_type.TEXT
        )
        assert get_response.status_code == 404, "Пользователь не был удален"
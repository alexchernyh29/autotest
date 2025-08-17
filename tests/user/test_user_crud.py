import os
import pytest
import requests
import allure
import json
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from faker import Faker

# Инициализация Faker
fake = Faker()

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

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

@pytest.fixture
def test_user():
    """Фикстура для создания тестового пользователя"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        
        assert base_url is not None, "API_URL не найден в .env файле"
        assert token is not None, "TOKEN_ID не найден в .env файле"
        
        user_data = {
            "fio": fake.name(),
            "login": fake.user_name(),
            "password": fake.password(length=12, special_chars=True),
            "mail": fake.email(),
            "phone": f"79{str(fake.random_number(digits=9))}",
            "role_id": 1,
            "tenant_id": 123,
            "is_manager": fake.random_element(elements=(0, 1))
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
                "tockenId": token
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

def test_update_user_with_faker(test_user):
    """PUT Обновление данных пользователя с использованием Faker"""
    with allure.step("Подготовка данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        user_id = test_user

        # Сначала проверяем, что пользователь существует
        check_response = requests.get(
            f"{base_url}/api/v1/user/{user_id}",
            headers={"tockenId": token}
        )
        log_curl(check_response.request, check_response)
        assert check_response.status_code == 200, (
            f"Пользователь не найден перед обновлением. Status: {check_response.status_code}"
        )

        # Генерация случайных данных для обновления
        update_data = {
            "fio": fake.name(),
            "login": fake.user_name()[:20],  # Ограничение длины, если есть
            "mail": fake.email(),
            "phone": f"79{str(fake.random_number(digits=9))}",
            "role_id": fake.random_int(min=1, max=5),
            "tenant_id": 123,
            "is_manager": fake.random_element(elements=(0, 1))
        }

        allure.attach(
            json.dumps(update_data, indent=2),
            name="Update Data (Faker)",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Отправка PUT запроса"):
        # Логируем полный URL для отладки
        full_url = f"{base_url}/api/v1/user/{user_id}"
        allure.attach(
            f"Full URL: {full_url}",
            name="Request URL",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = requests.put(
            full_url,
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "tockenId": token  # Обратите внимание на регистр (tockenId vs tockenid)
            },
            json=update_data
        )
        log_curl(response.request, response)
        
        # Детальный анализ ошибки
        if response.status_code != 200:
            error_details = {
                "status_code": response.status_code,
                "response_text": response.text,
                "request_url": full_url,
                "user_id": user_id,
                "headers": dict(response.request.headers)
            }
            allure.attach(
                json.dumps(error_details, indent=2),
                name="Error Details",
                attachment_type=allure.attachment_type.JSON
            )
        
        assert response.status_code == 200, (
            f"Ожидался код 200, получен {response.status_code}. "
            f"Response: {response.text}"
        )

    with allure.step("Проверка обновленных данных"):
        get_response = requests.get(
            f"{base_url}/api/v1/user/{user_id}",
            headers={"tockenId": token}
        )
        log_curl(get_response.request, get_response)
        assert get_response.status_code == 200, "Не удалось получить данные пользователя после обновления"
        
        updated_user = get_response.json()
        
        verification_results = []
        for field, expected_value in update_data.items():
            actual_value = updated_user.get(field)
            match = str(expected_value) == str(actual_value)
            verification_results.append({
                "field": field,
                "expected": expected_value,
                "actual": actual_value,
                "match": match
            })
            
            assert match, (
                f"Поле {field} не соответствует ожидаемому значению. "
                f"Ожидалось: {expected_value}, Получено: {actual_value}"
            )
        
        allure.attach(
            json.dumps(verification_results, indent=2),
            name="Verification Results",
            attachment_type=allure.attachment_type.JSON
        )

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
                "tockenId": token
            }
        )
        log_curl(response.request, response)
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"

    with allure.step("Проверка удаления пользователя"):
        get_response = requests.get(
            f"{base_url}/api/v1/user/{user_id}",
            headers={"tockenId": token}
        )
        log_curl(get_response.request, get_response)
        assert get_response.status_code == 404, "Пользователь не был удален"
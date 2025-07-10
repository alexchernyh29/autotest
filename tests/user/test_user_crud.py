import os
import pytest
import requests
from dotenv import load_dotenv, set_key
import random
import string
from pathlib import Path
from config import ENV_FILE

# Определяем путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

# Фикстура для создания тестового пользователя
@pytest.fixture
def test_user():
    """Фикстура для создания тестового пользователя"""
    # Загружаем переменные с явным указанием пути
    load_dotenv(ENV_FILE)
    
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")
    
    # Проверяем, что переменные загрузились
    assert base_url is not None, "API_URL не найден в .env файле"
    assert token is not None, "TOKEN_ID не найден в .env файле"
    
    # Генерация случайных данных
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
    
    # Создание пользователя
    response = requests.post(
        f"{base_url}/api/v1/user",
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "tockenid": token  # Обратите внимание на опечатку в API (tockenid вместо tokenid)
        },
        json=user_data
    )
    
    assert response.status_code == 200, f"Ошибка создания пользователя: {response.text}"
    user_id = response.json()["id"]
    
    yield user_id  # Возвращаем ID созданного пользователя
    
    # Удаление пользователя после теста
    requests.delete(
        f"{base_url}/api/v1/user/{user_id}",
        headers={"tockenid": token}
    )

@pytest.mark.run(order=2)
def test_get_user(test_user):
    """GET Получение данных пользователя /api/v1/user/(id)"""
    load_dotenv(ENV_FILE)
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")
    user_id = test_user
    
    response = requests.get(
        f"{base_url}/api/v1/user/{user_id}",
        headers={
            "accept": "*/*",
            "tockenid": token
        }
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_update_user(test_user):
    """PUT Обновление данных пользователя /api/v1/user/(id)"""
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
    
    response = requests.put(
        f"{base_url}/api/v1/user/{user_id}",
        headers={
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "tockenid": token
        },
        json=update_data
    )
    
    assert response.status_code == 200
    
    # Проверяем, что данные обновились
    get_response = requests.get(
        f"{base_url}/api/v1/user/{user_id}",
        headers={"tockenid": token}
    )
    assert get_response.json()["fio"] == "Updated Name"

def test_delete_user(test_user):
    """DELETE Удаление пользователя /api/v1/user/(id)"""
    load_dotenv(ENV_FILE)
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")
    user_id = test_user
    
    response = requests.delete(
        f"{base_url}/api/v1/user/{user_id}",
        headers={
            "accept": "*/*",
            "tockenid": token
        }
    )
    
    assert response.status_code == 200
    
    # Проверяем, что пользователь удален
    get_response = requests.get(
        f"{base_url}/api/v1/user/{user_id}",
        headers={"tockenid": token}
    )
    assert get_response.status_code == 404
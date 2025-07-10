import os
import requests
from dotenv import load_dotenv, set_key
import random
import string
from datetime import datetime
from config import ENV_FILE
import pytest

@pytest.mark.run(order=3)
def generate_random_user():
    """Генерация случайных данных пользователя"""
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    timestamp = datetime.now().strftime("%m%d%H%M%S")
    
    return {
        "fio": f"Autotest User {rand_str}",
        "login": f"autotest_{timestamp}",
        "password": f"P@ss_{rand_str}",
        "mail": f"autotest+{timestamp}@example.com",
        "phone": f"79{random.randint(1000000, 9999999)}",
        "role_id": 1,
        "tenant_id": 123,
        "is_manager": 1
    }

def test_create_user_and_save_id():
    """Тест создания пользователя с сохранением ID"""
    load_dotenv(ENV_FILE)
    
    # 1. Подготовка запроса
    url = f"{os.getenv('API_URL')}/api/v1/user"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "tockenid": os.getenv("TOKEN_ID")  # Используем сохранённый токен
    }
    user_data = generate_random_user()
    
    # 2. Отправка запроса
    response = requests.post(url, headers=headers, json=user_data)
    assert response.status_code == 200, f"Ошибка создания пользователя: {response.text}"
    
    # 3. Извлечение и сохранение ID
    response_data = response.json()
    user_id = response_data.get("id")
    assert user_id, "ID пользователя не найден в ответе"
    
    # 4. Сохранение в .env
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    set_key(env_path, "CREATED_USER_ID", str(user_id))
    set_key(env_path, "CREATED_USER_LOGIN", user_data["login"])  # Дополнительно сохраняем логин
    
    print(f"\nСоздан пользователь:\n"
          f"ID: {user_id}\n"
          f"Login: {user_data['login']}\n"
          f"mail: {user_data['mail']}")
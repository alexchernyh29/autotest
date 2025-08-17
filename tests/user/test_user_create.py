import os
import requests
from dotenv import load_dotenv, find_dotenv, set_key
import random
import string
from datetime import datetime
from config import ENV_FILE
import pytest
import allure
import json

def test_create_user_and_save_id():
    """Тест создания пользователя с сохранением ID"""
    with allure.step("1. Подготовка тестовых данных"):
        def generate_random_user():
            rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            timestamp = datetime.now().strftime("%m%d%H%M%S")
            
            user_data = {
                "fio": f"Autotest User {rand_str}",
                "login": f"autotest_{timestamp}",
                "password": f"P@ss_{rand_str}",
                "mail": f"autotest+{timestamp}@example.com",
                "phone": f"79{random.randint(1000000, 9999999)}",
                "role_id": 1,
                "tenant_id": 123,
                "is_manager": 1
            }
            
            allure.attach(
                json.dumps(user_data, indent=2, ensure_ascii=False),
                name="Generated user data",
                attachment_type=allure.attachment_type.JSON
            )
            return user_data
        
        user_data = generate_random_user()

    with allure.step("2. Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv('API_URL')
        token = os.getenv("TOKEN_ID")
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    with allure.step("3. Формирование запроса"):
        url = f"{base_url}/api/v1/user"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "tockenid": token
        }
        
        # Логирование cURL
        curl_command = (
            f"curl -X POST '{url}' \\\n"
            f"  -H 'accept: application/json' \\\n"
            f"  -H 'content-type: application/json' \\\n"
            f"  -H 'tockenid: {token}' \\\n"
            f"  -d '{json.dumps(user_data)}'"
        )
        allure.attach(
            curl_command,
            name="cURL request",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("4. Отправка запроса на создание пользователя"):
        response = requests.post(url, headers=headers, json=user_data)
        
        # Логирование ответа
        allure.attach(
            f"Status Code: {response.status_code}\n\nResponse Body:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}",
            name="API Response",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("5. Проверка ответа"):
        assert response.status_code == 200, (
            f"Ожидался код 200, получен {response.status_code}\n"
            f"Response: {response.text}"
        )
        
        response_data = response.json()
        assert "id" in response_data, "В ответе отсутствует поле 'id'"
        
        user_id = str(response_data["id"])
        allure.attach(
            f"Создан пользователь с ID: {user_id}",
            name="User ID",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("6. Сохранение данных в .env"):
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        set_key(env_path, "CREATED_USER_ID", user_id)
        set_key(env_path, "CREATED_USER_LOGIN", user_data["login"])
        
        allure.attach(
            f"CREATED_USER_ID={user_id}\nCREATED_USER_LOGIN={user_data['login']}",
            name="Saved to .env",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("7. Вывод информации о созданном пользователе"):
        result_message = (
            f"Успешно создан пользователь:\n"
            f"ID: {user_id}\n"
            f"Login: {user_data['login']}\n"
            f"Email: {user_data['mail']}\n"
            f"Phone: {user_data['phone']}\n"
            f"FIO: {user_data['fio']}"
        )
        allure.attach(
            result_message,
            name="User creation summary",
            attachment_type=allure.attachment_type.TEXT
        )
        print(f"\n{result_message}")
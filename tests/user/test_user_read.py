import os
import requests
import pytest
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@pytest.mark.run(order=4)
def test_get_user():
    """Получение данных пользователя по ID"""
    # Загрузка переменных окружения
    load_dotenv(ENV_FILE)
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")
    test_user_id = os.getenv("CREATED_USER_ID")

    # Проверка наличия обязательных переменных
    assert base_url, "API_URL не задан в .env"
    assert token, "TOKEN_ID не задан в .env"
    assert test_user_id, "CREATED_USER_ID не задан в .env"

    # Формирование запроса
    headers = {
        "accept": "*/*",
        "tockenid": token  # Обратите внимание на опечатку в API (tockenid вместо tokenid)
    }
    
    # Варианты URL для тестирования
    test_urls = [
        f"{base_url}/api/v1/user/{test_user_id}",
    ]

    for url in test_urls:
        print(f"\nПробуем URL: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Успешный URL: {url}")
            print(f"Данные пользователя: {user_data}")
            return
        
        print(f"Ошибка {response.status_code}: {response.text}")

    pytest.fail("Не удалось найти пользователя")
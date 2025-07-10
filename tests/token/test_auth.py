import os
import requests
from dotenv import load_dotenv, set_key
import pytest
from config import ENV_FILE

@pytest.mark.run(order=1)
def test_get_and_save_token():
    """Тест: получение токена и сохранение в .env"""
    load_dotenv(ENV_FILE)
    
    # Проверка загруженных переменных
    api_url = os.getenv("API_URL")
    assert api_url, "API_URL не задан в .env"
    
    url = f"{api_url}/api/v1/tocken"
    params = {
        "login": os.getenv("API_LOGIN"),
        "password": os.getenv("API_PASSWORD"),
        "timeoutlive": os.getenv("TOKEN_TIMEOUT"),
        "domain": os.getenv("API_DOMAIN")
    }
    headers = {"accept": "application/json"}

    print(f"\nОтправка запроса на: {url}")  # Для отладки
    
    response = requests.post(url, params=params, headers=headers)
    assert response.status_code == 200, f"Ошибка: {response.text}"
    
    token = response.json().get("tockenID")
    assert token, "Токен не получен в ответе"
    
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    set_key(env_path, "TOKEN_ID", token)
    
    print(f"\nТокен получен: {token[:10]}...")

def test_use_saved_token():
    """Пример использования сохранённого токена"""
    load_dotenv(override=True)  # Перезагружаем .env
    token = os.getenv("TOKEN_ID")
    assert token, "Токен не загружен из .env!"
    print(f"\nТокен из .env: {token[:10]}...")
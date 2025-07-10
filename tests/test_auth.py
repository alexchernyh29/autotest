import os
import requests
from dotenv import load_dotenv, set_key
import pytest

# Фикстура для загрузки env один раз на все тесты
@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()

def test_get_and_save_token():
    """Тест: получение токена и сохранение в .env"""
    # Формируем URL и параметры
    url = f"{os.getenv('API_URL')}/api/v1/tocken"
    params = {
        "login": os.getenv("API_LOGIN"),
        "password": os.getenv("API_PASSWORD"),
        "timeoutlive": os.getenv("TOKEN_TIMEOUT"),
        "domain": os.getenv("API_DOMAIN")
    }
    headers = {"accept": "application/json"}

    # Отправляем запрос
    response = requests.post(url, params=params, headers=headers)
    
    # Проверяем статус
    assert response.status_code == 200, f"Ошибка: статус {response.status_code}"
    
    # Получаем токен
    response_data = response.json()
    token = response_data.get("tockenID")  # Обратите внимание на "tockenID"
    assert token, "Токен не найден в ответе!"
    
    # Сохраняем токен в .env
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    set_key(env_path, "TOKEN_ID", token)
    
    # Принудительно перезагружаем .env
    load_dotenv(override=True)
    
    print(f"\nТокен успешно получен: {token[:50]}...")

def test_use_saved_token():
    """Пример использования сохранённого токена"""
    token = os.getenv("TOKEN_ID")
    assert token, "Токен не загружен из .env!"
    print(f"\nИспользуем токен: {token[:50]}...")
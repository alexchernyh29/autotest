import os
import requests
import allure
import pytest
from dotenv import load_dotenv, find_dotenv, set_key
from config import ENV_FILE

def test_get_and_save_token():
    """Тест: получение токена и сохранение в .env"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        
        # Проверка загруженных переменных
        api_url = os.getenv("API_URL")
        api_login = os.getenv("API_LOGIN")
        api_password = os.getenv("API_PASSWORD")
        timeout = os.getenv("TOKEN_TIMEOUT")
        domain = os.getenv("API_DOMAIN")
        
        assert api_url, "API_URL не задан в .env"
        assert api_login, "API_LOGIN не задан в .env"
        assert api_password, "API_PASSWORD не задан в .env"

    with allure.step("Формирование запроса"):
        url = f"{api_url}/api/v1/tocken"
        params = {
            "login": api_login,
            "password": api_password,
            "timeoutlive": timeout,
            "domain": domain
        }
        headers = {"accept": "application/json"}
        
        allure.attach(
            f"curl -X POST '{url}?login={api_login}&password=*****&timeoutlive={timeout}&domain={domain}' "
            f"-H 'accept: application/json'",
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Отправка запроса на получение токена"):
        response = requests.post(url, params=params, headers=headers)
        
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert response.status_code == 200, f"Ошибка: {response.text}"

    with allure.step("Извлечение и проверка токена"):
        token = response.json().get("tockenID")
        assert token, "Токен не получен в ответе"
        
        allure.attach(
            f"Полученный токен (первые 10 символов): {token[:10]}...",
            name="Токен",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Сохранение токена в .env файл"):
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        set_key(env_path, "TOKEN_ID", token)
        
        allure.attach(
            f"Токен сохранен в файл: {env_path}",
            name="Сохранение токена",
            attachment_type=allure.attachment_type.TEXT
        )

def test_use_saved_token():
    """Пример использования сохранённого токена"""
    with allure.step("Загрузка токена из .env файла"):
        load_dotenv(override=True)  # Перезагружаем .env
        token = os.getenv("TOKEN_ID")
        
        allure.attach(
            f"Токен из .env (первые 10 символов): {token[:10]}..." if token else "Токен не найден",
            name="Проверка токена",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert token, "Токен не загружен из .env!"
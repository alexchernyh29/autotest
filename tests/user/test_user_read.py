import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@allure.feature("Получение данных пользователя")
def test_get_user():
    """Получение данных пользователя по ID"""
    with allure.step("Подготовка тестовых данных"):
        # Загрузка переменных окружения
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        test_user_id = os.getenv("CREATED_USER_ID")

        # Проверка наличия обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert test_user_id, "CREATED_USER_ID не задан в .env"

    with allure.step("Формирование заголовков запроса"):
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(str(headers), name="Request Headers", attachment_type=allure.attachment_type.TEXT)

    # Варианты URL для тестирования
    test_urls = [
        f"{base_url}/api/v1/user/{test_user_id}",
    ]

    for url in test_urls:
        with allure.step(f"Отправка GET запроса на {url}"):
            allure.attach(f"curl -X GET '{url}' -H 'accept: */*' -H 'tockenid: {token}'", 
                         name="CURL команда", 
                         attachment_type=allure.attachment_type.TEXT)
            
            response = requests.get(url, headers=headers)
            
            with allure.step("Проверка ответа"):
                allure.attach(f"Status Code: {response.status_code}\nResponse: {response.text}", 
                             name="Response Details", 
                             attachment_type=allure.attachment_type.TEXT)
                
                if response.status_code == 200:
                    user_data = response.json()
                    allure.attach(str(user_data), 
                                 name="User Data", 
                                 attachment_type=allure.attachment_type.JSON)
                    
                    with allure.step("Проверка структуры ответа"):
                        assert isinstance(user_data, dict), "Ответ должен быть словарем"
                        assert "id" in user_data, "В ответе отсутствует поле id"
                        # Преобразуем test_user_id к int для сравнения
                        assert user_data["id"] == int(test_user_id), "ID пользователя не совпадает с ожидаемым"
                    
                    return
        
        pytest.fail("Не удалось найти пользователя")
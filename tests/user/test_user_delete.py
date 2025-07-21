import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import pytest
import allure
import json

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

def log_curl(request, response):
    """Логирование cURL команды и деталей запроса/ответа"""
    # Формирование cURL
    command = f"curl -X {request.method} '{request.url}'"
    for name, value in request.headers.items():
        command += f" \\\n  -H '{name}: {value}'"
    
    # Логирование в Allure
    with allure.step("Детали запроса"):
        allure.attach(
            f"Method: {request.method}\nURL: {request.url}\nHeaders: {json.dumps(dict(request.headers), indent=2)}",
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
            f"Status Code: {response.status_code}\nResponse: {response_body}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

def test_delete_user():
    """Тест удаления пользователя"""
    with allure.step("1. Подготовка данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        test_user_id = os.getenv("CREATED_USER_ID")
        
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert test_user_id, "CREATED_USER_ID не задан в .env"
        
        headers = {
            "accept": "*/*", 
            "tockenid": token
        }
        
        allure.attach(
            f"Удаляемый пользователь ID: {test_user_id}",
            name="User ID",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("2. Отправка DELETE запроса"):
        delete_response = requests.delete(
            f"{base_url}/api/v1/user/{test_user_id}",
            headers=headers
        )
        log_curl(delete_response.request, delete_response)
        
        assert delete_response.status_code == 200, (
            f"Ожидался код 200, получен {delete_response.status_code}\n"
            f"Ответ: {delete_response.text}"
        )

    with allure.step("3. Проверка удаления пользователя"):
        get_response = requests.get(
            f"{base_url}/api/v1/user/{test_user_id}",
            headers=headers
        )
        log_curl(get_response.request, get_response)
        
        allure.attach(
            f"Ожидаемый статус: 404\nПолученный статус: {get_response.status_code}",
            name="Deletion Verification",
            attachment_type=allure.attachment_type.TEXT
        )
        assert get_response.status_code == 404, "Пользователь все еще доступен"

    with allure.step("4. Финализация"):
        result_message = f"Пользователь {test_user_id} успешно удален"
        allure.attach(
            result_message,
            name="Test Result",
            attachment_type=allure.attachment_type.TEXT
        )
        print(f"\n{result_message}")
import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

def test_update_user():
    """Обновление данных пользователя с обязательными полями"""
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

    with allure.step("1. Получение текущих данных пользователя"):
        get_headers = {"tockenid": token, "accept": "*/*"}
        get_url = f"{base_url}/api/v1/user/{test_user_id}"
        
        allure.attach(
            f"curl -X GET '{get_url}' -H 'accept: */*' -H 'tockenid: {token}'",
            name="CURL команда для получения данных",
            attachment_type=allure.attachment_type.TEXT
        )
        
        get_response = requests.get(get_url, headers=get_headers)
        allure.attach(
            f"Status Code: {get_response.status_code}\nResponse: {get_response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert get_response.status_code == 200, "Не удалось получить данные пользователя"
        current_data = get_response.json()
        allure.attach(
            str(current_data),
            name="Текущие данные пользователя",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("2. Подготовка данных для обновления"):
        update_data = {
            "fio": "Новое ФИО",
            "login": current_data["login"],
            "mail": "updated.email@example.com",
            "phone": "79123456789",
            "role_id": current_data["role_id"],
            "tenant_id": current_data["tenant_id"],
            "is_manager": 1
        }
        allure.attach(
            str(update_data),
            name="Данные для обновления",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("3. Отправка запроса на обновление"):
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "tockenid": token
        }
        update_url = f"{base_url}/api/v1/user/{test_user_id}"
        
        allure.attach(
            f"curl -X PUT '{update_url}' -H 'accept: application/json' "
            f"-H 'content-type: application/json' -H 'tockenid: {token}' "
            f"-d '{str(update_data).replace("'", '"')}'",
            name="CURL команда для обновления",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = requests.put(update_url, headers=headers, json=update_data)
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert response.status_code == 200, f"Ошибка обновления: {response.text}"

    with allure.step("4. Проверка обновленных данных"):
        updated_response = requests.get(
            f"{base_url}/api/v1/user/{test_user_id}",
            headers={"tockenid": token}
        )
        updated_data = updated_response.json()
        allure.attach(
            str(updated_data),
            name="Обновленные данные пользователя",
            attachment_type=allure.attachment_type.JSON
        )
        
        with allure.step("Проверка полей"):
            assert updated_data["fio"] == update_data["fio"], "ФИО не обновилось"
            assert updated_data["mail"] == update_data["mail"], "Email не обновился"
            assert updated_data["phone"] == update_data["phone"], "Телефон не обновился"
        
        with allure.step("Вывод результатов обновления"):
            allure.attach(
                f"ID пользователя: {test_user_id}\n"
                f"Новое ФИО: {updated_data['fio']}\n"
                f"Новый email: {updated_data['mail']}\n"
                f"Новый телефон: {updated_data['phone']}",
                name="Результаты обновления",
                attachment_type=allure.attachment_type.TEXT
            )
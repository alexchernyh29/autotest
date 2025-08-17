import os
import requests
import pytest
import allure
import json
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Управление связями пользователь-организация")
class TestUserOrganizationLinks:
    """Тесты для работы со связями пользователей и организаций"""
    @allure.story("Получение связей пользователь-организация")
    @allure.title("Поиск связи пользователя с организацией")
    def test_get_users_by_organization(self):
        """Проверка получения связи пользователя с организацией"""
        # Подготовка тестовых данных
        with allure.step("Загрузка конфигурации"):
            load_dotenv(ENV_FILE)
            base_url = os.getenv("API_URL")
            token = os.getenv("TOKEN_ID")
            organization_id = os.getenv("ORGANIZATION_ID")

            assert base_url, "API_URL не задан в .env"
            assert token, "TOKEN_ID не задан в .env"
            assert organization_id, "ORGANIZATION_ID не задан в .env"

        # Формирование запроса
        with allure.step("Подготовка запроса"):
            headers = {
                "accept": "application/json",
                "tockenid": token
            }
            
            url = f"{base_url}/api/v1/user_organization_link/{organization_id}"
            
            allure.attach(
                json.dumps(headers, indent=2),
                name="Request Headers",
                attachment_type=allure.attachment_type.JSON
            )
            
            curl_cmd = f"curl -X GET '{url}' -H 'accept: application/json' -H 'tockenid: {token}'"
            allure.attach(curl_cmd, name="CURL", attachment_type=allure.attachment_type.TEXT)

        # Отправка запроса
        with allure.step("Отправка запроса"):
            response = requests.get(url, headers=headers)
            
            allure.attach(
                f"Status: {response.status_code}\nResponse: {response.text}",
                name="Response",
                attachment_type=allure.attachment_type.TEXT
            )

        # Проверки ответа
        with allure.step("Анализ ответа"):
            if response.status_code == 404:
                allure.attach(
                    "Связь не найдена (ожидаемо для новых организаций)",
                    name="Связь отсутствует",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip("Связь пользователя с организацией не найдена (ожидаемо)")
            
            assert response.status_code == 200, (
                f"Неожиданная ошибка. Status: {response.status_code}, Response: {response.text}"
            )
            
            try:
                link_data = response.json()
            except ValueError:
                pytest.fail("Невалидный JSON в ответе")
            
            assert isinstance(link_data, dict), "Ответ должен быть объектом связи"
            
            allure.attach(
                json.dumps(link_data, indent=2),
                name="Связь пользователь-организация",
                attachment_type=allure.attachment_type.JSON
            )

        # Проверка структуры данных
        with allure.step("Проверка данных"):
            required_fields = {
                "id": int,
                "user_id": int,
                "organization_id": int,
                "create_time": dict,
                "update_time": dict,
                "create_user_id": int,
                "update_user_id": int
            }
            
            for field, field_type in required_fields.items():
                assert field in link_data, f"Отсутствует обязательное поле: {field}"
                assert isinstance(link_data[field], field_type), (
                    f"Поле {field} имеет неверный тип. Ожидается: {field_type}, получено: {type(link_data[field])}"
                )
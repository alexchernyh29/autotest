# Возвращает список всех ролей для рендеринга биллинга /api/v1/billing/roles_render_billing
import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Рендеринг биллинговой роли")
def test_roles_render_billing():
    """Получение данных для рендеринга биллинговой роли"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    with allure.step("Формирование заголовков запроса"):
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(str(headers), name="Request Headers", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Формирование URL запроса"):
        url = f"{base_url}/api/v1/billing/roles_render_billing"
        allure.attach(f"curl --location '{url}' --header 'accept: application/json' --header 'tockenid: {token}'", 
                      name="CURL команда", 
                      attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Отправка GET запроса на {url}"):
        response = requests.get(url, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

            try:
                billing_data = response.json()
            except requests.exceptions.JSONDecodeError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(str(billing_data), name="Billing Role Data", attachment_type=allure.attachment_type.JSON)
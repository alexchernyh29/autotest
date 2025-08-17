# Возвращает полную информацию о связи тарифа и арендатора /api/v1/tariff_link_tenant/{id}
# tests/test_get_tariff_link_tenant.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Получение связи тарифа с арендатором")
def test_get_tariff_link_tenant():
    """Получение информации о связи тарифа с арендатором по ID"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        link_id = os.getenv("CREATED_LINK_TENANT_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert link_id, "CREATED_LINK_TENANT_ID не задан в .env. Укажите ID связи для теста."

        try:
            link_id = int(link_id)
        except ValueError:
            pytest.fail("CREATED_LINK_TENANT_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff_link_tenant/{link_id}"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step(f"Отправка GET-запроса на {url}"):
        curl_command = (
            f"curl -X GET '{url}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(
            curl_command,
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

        response = requests.get(url, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Ожидался статус 200, но получен {response.status_code}"

            try:
                link_data = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                link_data,
                name="Tariff Link Tenant Data",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(link_data, dict), "Ответ должен быть объектом (dict)"
                assert "id" in link_data, "Отсутствует поле 'id'"
                assert "tariff_id" in link_data, "Отсутствует поле 'tariff_id'"
                assert "tenant_id" in link_data, "Отсутствует поле 'tenant_id'"
                assert "name" in link_data, "Отсутствует поле 'name'"
                assert "type_tariff" in link_data, "Отсутствует поле 'type_tariff'"

                # Дополнительные поля (опционально — раскомментируй, если ожидаются)
                # assert "description" in link_data, "Отсутствует поле 'description'"
                # assert "is_active" in link_data, "Отсутствует поле 'is_active'"

                # Проверка соответствия ID
                assert link_data["id"] == link_id, \
                    f"Ожидалась связь с ID={link_id}, но получен ID={link_data.get('id')}"
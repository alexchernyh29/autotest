# Добавление пользователя в организацию /api/v1/user_organization_link?user_id={id}&organization_id={id}
# tests/users/test_create_user_organization_link.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, set_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Создание связи пользователя с организацией")
def test_create_user_organization_link():
    """Создание связи между пользователем и организацией"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        user_id = os.getenv("TEST_USER_ID")
        org_id = os.getenv("ORGANIZATION_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert user_id, "TEST_USER_ID не задан в .env"
        assert org_id, "ORGANIZATION_ID не задан в .env"

        try:
            user_id = int(user_id)
            org_id = int(org_id)
        except ValueError:
            pytest.fail("TEST_USER_ID и ORGANIZATION_ID должны быть числами")

    url = f"{base_url}/api/v1/user_organization_link"
    headers = {
        "accept": "*/*",
        "tockenid": token
    }

    # Параметры передаются в URL (query params)
    params = {
        "user_id": user_id,
        "organization_id": org_id
    }

    with allure.step(f"Отправка POST-запроса на {url} с user_id={user_id} и organization_id={org_id}"):
        curl_command = (
            f"curl -X POST '{url}?user_id={user_id}&organization_id={org_id}' "
            f"-H 'accept: */*' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(
            curl_command,
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            str(params),
            name="Query Parameters",
            attachment_type=allure.attachment_type.JSON
        )

        allure.attach(
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

        response = requests.post(url, params=params, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code in [200, 201], \
                f"Ожидался статус 200 или 201, но получен {response.status_code}"

            try:
                response_json = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                response_json,
                name="Response (User-Org Link)",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(response_json, dict), "Ответ должен быть объектом"
                assert "id" in response_json, "В ответе отсутствует поле 'id'"
                assert response_json["user_id"] == user_id, "user_id не совпадает"
                assert response_json["organization_id"] == org_id, "organization_id не совпадает"

            created_link_id = response_json["id"]
            with allure.step(f"Сохранение CREATED_USER_ORG_LINK_ID={created_link_id} в .env"):
                set_key(ENV_FILE, "CREATED_USER_ORG_LINK_ID", str(created_link_id))
                allure.attach(
                    f"CREATED_USER_ORG_LINK_ID={created_link_id}",
                    name="ID созданной связи",
                    attachment_type=allure.attachment_type.TEXT
                )
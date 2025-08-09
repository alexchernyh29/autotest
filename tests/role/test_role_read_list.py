# Получение списка ролей /api/v1/roles?by_role_id={id}
# tests/role/test_roles_read_all.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@allure.feature("Получение списка ролей")
def test_get_all_roles():
    """Получение списка всех ролей из системы"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    url = f"{base_url}/api/v1/roles"
    headers = {
        "accept": "*/*",
        "tockenid": token
    }

    with allure.step(f"Отправка GET-запроса на {url}"):
        curl_command = (
            f"curl -X GET '{url}' "
            f"-H 'accept: */*' "
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
                roles_list = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                roles_list,
                name="Roles List Response",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(roles_list, list), "Ожидался массив ролей"
                assert len(roles_list) > 0, "Список ролей пуст. Проверьте данные в API."

                found_ids = []
                required_fields = {"id", "name", "code"}

                for role in roles_list:
                    with allure.step(f"Проверка роли с ID={role.get('id')}"):
                        assert isinstance(role, dict), "Каждая роль должна быть объектом"
                        assert required_fields.issubset(role.keys()), \
                            f"Роль должна содержать поля: {required_fields}. Получено: {list(role.keys())}"

                        # Проверка типов
                        assert isinstance(role["id"], int), "Поле 'id' должно быть числом"
                        assert isinstance(role["name"], str) and len(role["name"].strip()) > 0, \
                            "Поле 'name' должно быть непустой строкой"
                        assert isinstance(role["code"], str) and len(role["code"].strip()) > 0, \
                            "Поле 'code' должно быть непустой строкой"

                        found_ids.append(role["id"])

                with allure.step(f"Найдены роли с ID: {sorted(found_ids)}"):
                    pass  # Отображается в отчёте

                # Опционально: проверка, что ID уникальны
                assert len(found_ids) == len(set(found_ids)), "ID ролей должны быть уникальными"
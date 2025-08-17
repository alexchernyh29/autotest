# Получение списка ролей /api/v1/roles
# tests/role/test_role_read_list.py

import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


def get_auth_token(login: str, password: str, timeoutlive: int, domain: str) -> str:
    """Получение токена аутентификации"""
    base_url = os.getenv("API_URL")
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {"accept": "application/json"}

    with allure.step("Получение токена аутентификации"):
        allure.attach(f"URL: {url}", "Request URL", allure.attachment_type.TEXT)
        allure.attach(json.dumps(params, indent=2), "Request Params", allure.attachment_type.JSON)
        allure.attach(json.dumps(headers, indent=2), "Request Headers", allure.attachment_type.JSON)

        response = requests.post(url, headers=headers, params=params)
        allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        allure.attach(response.text, "Response Body", allure.attachment_type.TEXT)

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


@allure.feature("Получение списка ролей")
def test_get_all_roles():
    """Получение списка всех ролей из системы и проверка, что их ровно 6"""
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    # Получаем токен
    with allure.step("Автоматическое получение токена"):
        try:
            token = get_auth_token(login, password, 600, domain)
            assert token, "Не удалось получить токен"
            allure.attach(token, "Полученный токен", allure.attachment_type.TEXT)
        except Exception as e:
            pytest.fail(f"Ошибка при получении токена: {e}")

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
        allure.attach(curl_command, "CURL команда", allure.attachment_type.TEXT)
        allure.attach(json.dumps(headers, indent=2), "Request Headers", allure.attachment_type.JSON)

        response = requests.get(url, headers=headers)

        allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        allure.attach(response.text, "Response Body", allure.attachment_type.TEXT)

    with allure.step("Проверка ответа"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, но получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

        try:
            roles_list = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        # ✅ Исправлено: передаём response.text, а не list
        allure.attach(
            response.text,
            name="Roles List Response",
            attachment_type=allure.attachment_type.JSON
        )

        with allure.step("Проверка структуры ответа"):
            assert isinstance(roles_list, list), "Ожидался массив ролей"
            assert len(roles_list) > 0, "Список ролей пуст. Проверьте данные в API."

            # ✅ Проверка, что ровно 6 ролей
            assert len(roles_list) == 6, f"Ожидалось 6 ролей, но получено {len(roles_list)}"

            found_ids = []
            # ✅ Судя по примеру, поля: id, name, system_name (а не code)
            required_fields = {"id", "name", "system_name"}

            for role in roles_list:
                with allure.step(f"Проверка роли с ID={role.get('id')}"):
                    assert isinstance(role, dict), "Каждая роль должна быть объектом"
                    missing = required_fields - role.keys()
                    assert not missing, f"Отсутствуют поля: {missing}. Получено: {list(role.keys())}"

                    # Проверка типов
                    assert isinstance(role["id"], int), "Поле 'id' должно быть числом"
                    assert isinstance(role["name"], str) and len(role["name"].strip()) > 0, \
                        "Поле 'name' должно быть непустой строкой"
                    assert isinstance(role["system_name"], str) and len(role["system_name"].strip()) > 0, \
                        "Поле 'system_name' должно быть непустой строкой"

                    found_ids.append(role["id"])

            with allure.step(f"Найдены ID ролей: {sorted(found_ids)}"):
                pass

            # Проверка уникальности ID
            assert len(found_ids) == len(set(found_ids)), "ID ролей должны быть уникальными"
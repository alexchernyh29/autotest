# Получение роли /api/v1/role/{id}
# tests/role/test_role_read_id.py

import os
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
        allure.attach(str(params), "Request Params", allure.attachment_type.JSON)
        allure.attach(str(headers), "Request Headers", allure.attachment_type.JSON)

        response = requests.post(url, headers=headers, params=params)
        allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
        allure.attach(response.text, "Response Body", allure.attachment_type.TEXT)

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


# 📚 Ожидаемые значения ролей
EXPECTED_ROLES = {
    1: {
        "name": "Пользователь Организации",
        "system_name": "ROLE_ORGANIZATION_USER"
    },
    2: {
        "name": "Владелец Организации",
        "system_name": "ROLE_ORGANIZATION_OWNER"
    },
    3: {
        "name": "Менеджер Тенанта",
        "system_name": "ROLE_TENANT_MANAGER"
    },
    4: {
        "name": "Инженер Тенанта",
        "system_name": "ROLE_TENANT_ENGINEER"
    },
    5: {
        "name": "Администратор Тенанта",
        "system_name": "ROLE_TENANT_ADMIN"
    },
    6: {
        "name": "Супер Администратор",
        "system_name": "ROLE_SUPER_ADMIN"
    }
}


@allure.feature("Получение ролей по ID")
class TestGetRoles:
    """Тестирование получения ролей по ID от 1 до 6"""

    def setup_class(self):
        """Подготовка данных: загрузка .env и получение токена"""
        load_dotenv(ENV_FILE)

        self.base_url = os.getenv("API_URL")
        self.login = os.getenv("API_LOGIN")
        self.password = os.getenv("API_PASSWORD")
        self.domain = os.getenv("API_DOMAIN")

        assert self.base_url, "API_URL не задан в .env"
        assert self.login, "API_LOGIN не задан в .env"
        assert self.password, "API_PASSWORD не задан в .env"
        assert self.domain, "API_DOMAIN не задан в .env"

        # Получаем токен
        with allure.step("Автоматическое получение токена"):
            try:
                self.token = get_auth_token(self.login, self.password, 600, self.domain)
                assert self.token, "Не удалось получить токен аутентификации"
                allure.attach(self.token, "Полученный токен", allure.attachment_type.TEXT)
            except Exception as e:
                pytest.fail(f"Ошибка при получении токена: {e}")

        self.headers = {
            "accept": "*/*",
            "tockenid": self.token
        }

    @allure.story("Отправка GET-запросов для ID от 1 до 6")
    @pytest.mark.parametrize("role_id", list(range(1, 7)))
    def test_get_role_by_id(self, role_id):
        """Получение роли по ID. Проверка точного соответствия name и system_name"""
        expected = EXPECTED_ROLES[role_id]

        url = f"{self.base_url}/api/v1/role/{role_id}"

        with allure.step(f"Отправка GET-запроса на {url}"):
            curl_command = (
                f"curl -X GET '{url}' "
                f"-H 'accept: */*' "
                f"-H 'tockenid: {self.token}'"
            )
            allure.attach(curl_command, "CURL команда", allure.attachment_type.TEXT)
            allure.attach(str(self.headers), "Request Headers", allure.attachment_type.JSON)

            response = requests.get(url, headers=self.headers)

            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
            allure.attach(response.text, "Response Body", allure.attachment_type.TEXT)

        with allure.step(f"Проверка ответа для role_id={role_id}"):
            if response.status_code == 200:
                try:
                    role_data = response.json()
                except ValueError:
                    pytest.fail(f"Ответ для role_id={role_id} не является валидным JSON")

                allure.attach(
                    response.text,
                    name="Role Data",
                    attachment_type=allure.attachment_type.JSON
                )

                with allure.step(f"Проверка структуры и значений для role_id={role_id}"):
                    assert isinstance(role_data, dict), "Ожидался объект (dict)"
                    assert "id" in role_data, "В ответе отсутствует поле 'id'"
                    assert "name" in role_data, "В ответе отсутствует поле 'name'"
                    assert "system_name" in role_data, "В ответе отсутствует поле 'system_name'"

                    # Проверка ID
                    assert role_data["id"] == role_id, (
                        f"ID в ответе ({role_data['id']}) не совпадает с запрашиваемым ({role_id})"
                    )

                    # ✅ Проверка точного совпадения name и system_name
                    assert role_data["name"] == expected["name"], (
                        f"Неверное имя роли: ожидается '{expected['name']}', "
                        f"получено '{role_data['name']}'"
                    )

                    assert role_data["system_name"] == expected["system_name"], (
                        f"Неверное system_name: ожидается '{expected['system_name']}', "
                        f"получено '{role_data['system_name']}'"
                    )

                    # Проверка типов
                    assert isinstance(role_data["name"], str) and len(role_data["name"].strip()) > 0, \
                        "Поле 'name' должно быть непустой строкой"
                    assert isinstance(role_data["system_name"], str) and len(role_data["system_name"].strip()) > 0, \
                        "Поле 'system_name' должно быть непустой строкой"

                with allure.step("✅ Роль проверена"):
                    allure.attach(
                        f"ID: {role_id}\n"
                        f"Name (RU): {expected['name']}\n"
                        f"System Name (EN): {expected['system_name']}",
                        "Ожидаемые значения",
                        allure.attachment_type.TEXT
                    )

            elif response.status_code == 404:
                with allure.step(f"Роль с ID={role_id} не найдена (404)"):
                    allure.attach(
                        f"Роль ID={role_id} не существует в системе.",
                        name="Результат",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    pytest.fail("Роль с таким ID должна существовать")
            elif response.status_code == 401:
                pytest.fail("Ошибка 401 Unauthorized — возможно, токен недействителен или устарел")
            elif response.status_code == 403:
                pytest.fail("Ошибка 403 Forbidden — доступ запрещён")
            else:
                pytest.fail(
                    f"Ожидался статус 200, 404, 401 или 403 для role_id={role_id}, но получен {response.status_code}"
                )
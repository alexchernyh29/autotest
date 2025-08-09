# Получение роли /api/v1/role/{id}
# tests/role/test_role_read_multiple.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


@allure.feature("Получение ролей по ID")
class TestGetRoles:
    """Тестирование получения ролей по ID от 1 до 6"""

    def setup_class(self):
        """Подготовка данных перед выполнением тестов"""
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

        self.base_url = base_url
        self.token = token
        self.headers = {
            "accept": "*/*",
            "tockenid": token
        }

    @allure.story("Отправка GET-запросов для ID от 1 до 6")
    @pytest.mark.parametrize("role_id", list(range(1, 7)))
    def test_get_role_by_id(self, role_id):
        """Получение роли по ID. Ожидается 200 или 404"""
        url = f"{self.base_url}/api/v1/role/{role_id}"

        with allure.step(f"Отправка GET-запроса на {url}"):
            curl_command = (
                f"curl -X GET '{url}' "
                f"-H 'accept: */*' "
                f"-H 'tockenid: {self.token}'"
            )
            allure.attach(
                curl_command,
                name="CURL команда",
                attachment_type=allure.attachment_type.TEXT
            )

            allure.attach(
                str(self.headers),
                name="Request Headers",
                attachment_type=allure.attachment_type.TEXT
            )

            response = requests.get(url, headers=self.headers)

            with allure.step(f"Проверка ответа для role_id={role_id}"):
                allure.attach(
                    f"Status Code: {response.status_code}\nResponse: {response.text}",
                    name="Response Details",
                    attachment_type=allure.attachment_type.TEXT
                )

                if response.status_code == 200:
                    try:
                        role_data = response.json()
                    except ValueError:
                        pytest.fail(f"Ответ для role_id={role_id} не является валидным JSON")

                    allure.attach(
                        role_data,
                        name="Role Data",
                        attachment_type=allure.attachment_type.JSON
                    )

                    with allure.step(f"Проверка структуры ответа для role_id={role_id}"):
                        assert isinstance(role_data, dict), "Ожидался объект (dict)"
                        assert "id" in role_data, "В ответе отсутствует поле 'id'"
                        assert "name" in role_data, "В ответе отсутствует поле 'name'"
                        assert "code" in role_data, "В ответе отсутствует поле 'code'"

                        assert role_data["id"] == role_id, \
                            f"ID в ответе ({role_data['id']}) не совпадает с запрашиваемым ({role_id})"

                        assert isinstance(role_data["name"], str) and len(role_data["name"].strip()) > 0, \
                            "Поле 'name' должно быть непустой строкой"
                        assert isinstance(role_data["code"], str) and len(role_data["code"].strip()) > 0, \
                            "Поле 'code' должно быть непустой строкой"

                elif response.status_code == 404:
                    with allure.step(f"Роль с ID={role_id} не найдена (404) — это может быть ожидаемым поведением"):
                        allure.attach(
                            f"Роль ID={role_id} не существует в системе.",
                            name="Результат",
                            attachment_type=allure.attachment_type.TEXT
                        )
                else:
                    # Другие статусы (например, 500) — ошибка
                    pytest.fail(
                        f"Ожидался статус 200 или 404 для role_id={role_id}, но получен {response.status_code}"
                    )
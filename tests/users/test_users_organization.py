import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@allure.feature("Получение связей пользователь-организация")
def test_get_users_by_organization():
    """Получение списка пользователей, привязанных к организации"""
    with allure.step("Подготовка тестовых данных"):
        # Загрузка переменных окружения
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        organization_id = os.getenv("ORGANIZATION_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert organization_id, "ORGANIZATION_ID не задан в .env"

    with allure.step("Формирование заголовков запроса"):
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step(f"Формирование URL и отправка GET запроса"):
        url = f"{base_url}/api/v1/user_organization_link/{organization_id}"

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

        response = requests.get(url, headers=headers)

    with allure.step("Проверка ответа от сервера"):
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

        links_data = response.json()

        allure.attach(
            str(links_data),
            name="Список связей пользователь-организация",
            attachment_type=allure.attachment_type.JSON
        )

        with allure.step("Валидация структуры ответа"):
            assert isinstance(links_data, list), "Ответ должен быть списком связей"

            if len(links_data) > 0:
                first_link = links_data[0]
                with allure.step("Проверка структуры первой записи (пользователь-организация)"):
                    expected_fields = [
                        "id", "user_id", "organization_id", "tenant_id",
                        "created_at", "updated_at", "is_active"
                    ]
                    for field in expected_fields:
                        assert field in first_link, f"В объекте связи отсутствует поле: {field}"

                    # Проверка типов
                    assert isinstance(first_link["id"], int), "ID связи должен быть числом"
                    assert isinstance(first_link["user_id"], int), "user_id должен быть числом"
                    assert isinstance(first_link["organization_id"], int), "organization_id должен быть числом"
                    assert isinstance(first_link["is_active"], (bool, int)), "is_active должно быть булевым или числом"
                    assert first_link["organization_id"] == int(organization_id), \
                        "organization_id в ответе не соответствует запрошенному"

                # Дополнительно: можно проверить, что все элементы имеют правильный organization_id
                with allure.step("Проверка, что все записи относятся к указанной организации"):
                    for link in links_data:
                        assert link["organization_id"] == int(organization_id), \
                            f"Найдена запись с неверным organization_id: {link['organization_id']}"
            else:
                allure.attach(
                    "Список пользователей в организации пуст.",
                    name="Примечание",
                    attachment_type=allure.attachment_type.TEXT
                )
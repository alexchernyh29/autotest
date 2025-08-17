# Позволяет обновить информацию о связи тарифа с организацией /api/v1/tariff_link_organization/{id}
# tests/test_update_tariff_link_organization.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv, set_key
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Обновление связи тарифа с организацией")
def test_update_tariff_link_organization():
    """Обновление информации о связи между тарифом и организацией"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        link_id = os.getenv("CREATED_LINK_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert link_id, "CREATED_LINK_ID не задан в .env. Запустите сначала test_create_tariff_link_organization.py"

        try:
            link_id = int(link_id)
        except ValueError:
            pytest.fail("CREATED_LINK_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff_link_organization/{link_id}"
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
        "tockenid": token
    }

    # Обновлённые данные
    payload = {
        "tariff_id": 123,
        "tenant_id": 456,
        "is_organization": True,
        "name": "Название организации",
        "description": "Описание связи с организацией",
        "type_tariff": 1
    }

    with allure.step(f"Отправка PUT-запроса на {url} для обновления связи"):
        curl_command = (
            f"curl -X PUT '{url}' "
            f"-H 'accept: */*' "
            f"-H 'Content-Type: application/json' "
            f"-H 'tockenid: {token}' "
            f"-d '{str(payload).replace(' ', '').replace("'", '"')}'"
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

        allure.attach(
            payload,
            name="Request Body (JSON)",
            attachment_type=allure.attachment_type.JSON
        )

        response = requests.put(url, json=payload, headers=headers)

        with allure.step("Проверка ответа на обновление"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Ожидался статус 200, но получен {response.status_code}"

            try:
                updated_data = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                updated_data,
                name="Updated Link Data",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка, что данные обновились корректно"):
                assert updated_data.get("id") == link_id, "ID связи не совпадает"
                assert updated_data.get("tariff_id") == payload["tariff_id"], "tariff_id не обновился"
                assert updated_data.get("tenant_id") == payload["tenant_id"], "tenant_id не обновился"
                assert updated_data.get("is_organization") is True, "is_organization должно быть true"
                assert updated_data.get("name") == payload["name"], "Имя не обновилось"
                assert updated_data.get("description") == payload["description"], "Описание не обновилось"
                assert updated_data.get("type_tariff") == payload["type_tariff"], "type_tariff не обновился"

    # Дополнительная проверка: GET-запрос для подтверждения изменений
    with allure.step("Дополнительная проверка: GET-запрос для подтверждения обновления"):
        get_response = requests.get(url, headers={"accept": "*/*", "tockenid": token})
        assert get_response.status_code == 200, "GET после обновления вернул не 200"

        actual_data = get_response.json()
        assert actual_data.get("name") == payload["name"], "Имя не сохранилось после обновления"
        assert actual_data.get("description") == payload["description"], "Описание не сохранилось"
        assert actual_data.get("type_tariff") == payload["type_tariff"], "type_tariff не сохранился"
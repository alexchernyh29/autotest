import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Получение связей пула атомов для сервиса")
def test_get_service_pool_link_atoms_by_service_id():
    """Получение связей пула атомов по service_id из переменной окружения"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        service_id = os.getenv("SERVICE_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert service_id, "SERVICE_ID не задан в .env"

    with allure.step("Формирование заголовков запроса"):
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(str(headers), name="Request Headers", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Формирование URL запроса"):
        url = f"{base_url}/api/v1/billing/service_pool_link_atoms"
        params = {"by_service_id": service_id}
        curl_command = (
            f"curl --location '{url}?by_service_id={service_id}' "
            f"--header 'accept: application/json' "
            f"--header 'tockenid: {token}'"
        )
        allure.attach(curl_command, name="CURL команда", attachment_type=allure.attachment_type.TEXT)

    with allure.step(f"Отправка GET запроса на {url} с параметрами {params}"):
        response = requests.get(url, headers=headers, params=params)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

            try:
                link_atoms_data = response.json()
            except requests.exceptions.JSONDecodeError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(str(link_atoms_data), name="Pool Link Atoms Data", attachment_type=allure.attachment_type.JSON)

            with allure.step("Проверка структуры ответа"):
                assert isinstance(link_atoms_data, list), "Ответ должен быть списком связей"

                if link_atoms_data:
                    first_record = link_atoms_data[0]
                    assert isinstance(first_record, dict), "Каждая запись должна быть словарём"
                    expected_fields = {"id", "service_id", "pool_id", "atom_id", "created_at"}
                    record_keys = set(first_record.keys())
                    assert record_keys & expected_fields, \
                        f"Запись должна содержать хотя бы одно из ключевых полей: {expected_fields}"
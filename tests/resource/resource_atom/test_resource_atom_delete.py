# Удаляет атом ресурса /api/v1/resource_atom/{id}
import os
import pytest
import requests
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


def get_auth_token(login, password, timeoutlive, domain):
    """
    Получение токена аутентификации
    """
    base_url = os.getenv("API_URL")
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {
        "accept": "application/json"
    }

    with allure.step("Отправка запроса для получения токена"):
        allure.attach(f"URL: {url}", name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(params), name="Request Params", attachment_type=AttachmentType.TEXT)

        response = requests.post(url, headers=headers, params=params)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    response.raise_for_status()
    token_data = response.json()
    return token_data.get("tockenID")


@allure.story("Удаление атомарного ресурса по ID (DELETE)")
def test_delete_resource_atom_by_id():
    """
    Тест удаления атомарного ресурса через DELETE /api/v1/resource_atom/{id}
    Проверяет:
    1. Успешный статус-код (200, 204 или 200 с флагом success)
    2. Отсутствие тела или корректный ответ об удалении
    3. Возможную проверку через GET после удаления (опционально)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        resource_atom_id = os.getenv("RESOURCE_ATOM_ID", "1")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert resource_atom_id, "RESOURCE_ATOM_ID не задан"

    try:
        resource_atom_id = int(resource_atom_id)
        assert resource_atom_id > 0, "ID ресурса должно быть положительным целым числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_ATOM_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для удаления resource_atom (ID={resource_atom_id})"):
        url = f"{base_url}/api/v1/resource_atom/{resource_atom_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка DELETE-запроса на удаление ресурса"):
        response = requests.delete(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        # Обычные статусы при успешном удалении: 200 OK, 204 No Content
        expected_statuses = [200, 204]
        assert response.status_code in expected_statuses, (
            f"Ошибка при удалении resource_atom. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

        if response.status_code == 204:
            with allure.step("Статус 204 No Content — тело ответа должно быть пустым"):
                assert not response.text.strip(), "Ожидалось пустое тело при статусе 204"
        elif response.status_code == 200:
            with allure.step("Статус 200 — проверка тела ответа"):
                if response.text.strip():
                    try:
                        data = response.json()
                        allure.attach(str(data), name="Response JSON", attachment_type=AttachmentType.JSON)
                        # Пример: {"success": true} или {"message": "deleted"}
                        assert data.get("success") is True or "delete" in str(data).lower()
                    except ValueError:
                        # Если не JSON, можно просто залогировать
                        allure.attach(response.text, name="Non-JSON Response", attachment_type=AttachmentType.TEXT)
                else:
                    allure.attach("Тело пустое", name="Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Опциональная проверка: ресурс больше не доступен (GET)"):
        get_url = f"{base_url}/api/v1/resource_atom/{resource_atom_id}"
        get_headers = {
            "accept": "application/json",
            "tockenid": token
        }
        verification_response = requests.get(get_url, headers=get_headers)

        allure.attach(
            str(verification_response.status_code),
            name="GET после DELETE — статус",
            attachment_type=AttachmentType.TEXT
        )

        if verification_response.status_code == 404:
            allure.attach("Ресурс успешно удалён и больше не доступен (404)", name="Проверка", attachment_type=AttachmentType.TEXT)
        elif verification_response.status_code == 200:
            pytest.fail("Ресурс всё ещё доступен после DELETE — удаление не произошло")
        else:
            allure.attach(
                f"Неожиданный статус при проверке: {verification_response.status_code}",
                name="Предупреждение",
                attachment_type=AttachmentType.TEXT
            )

    with allure.step("Тест завершён: ресурс успешно удалён"):
        allure.attach(
            f"Удалён resource_atom с ID={resource_atom_id}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
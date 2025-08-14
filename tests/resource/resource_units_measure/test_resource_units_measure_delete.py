# Удаляет единицу измерения ресурсов /api/v1/resource_unit_measure/{id}
import os
import pytest
import requests
import allure
from dotenv import load_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


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


@allure.story("Удаление единицы измерения по ID (DELETE)")
def test_delete_resource_unit_measure_by_id():
    """
    Тест удаления единицы измерения через DELETE /api/v1/resource_unit_measure/{id}
    Проверяет:
    1. Успешный статус (200 или 204)
    2. Отсутствие тела при 204
    3. Опционально: проверка, что ресурс больше не доступен (GET → 404)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        unit_id = os.getenv("RESOURCE_UNIT_MEASURE_ID", "123112")  # Можно задать в .env

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert unit_id, "RESOURCE_UNIT_MEASURE_ID не задан"

    try:
        unit_id = int(unit_id)
        assert unit_id > 0, "ID единицы измерения должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_UNIT_MEASURE_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для удаления единицы измерения (ID={unit_id})"):
        url = f"{base_url}/api/v1/resource_unit_measure/{unit_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка DELETE-запроса"):
        response = requests.delete(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        # API может возвращать 200 OK или 204 No Content при успешном удалении
        assert response.status_code in [200, 204], (
            f"Ошибка при удалении единицы измерения. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

        if response.status_code == 204:
            with allure.step("Статус 204 — тело должно быть пустым"):
                assert not response.text.strip(), "Ожидалось пустое тело при статусе 204"
        elif response.status_code == 200:
            with allure.step("Статус 200 — проверка тела ответа (опционально)"):
                if response.text.strip():
                    try:
                        data = response.json()
                        allure.attach(str(data), name="Response JSON", attachment_type=AttachmentType.JSON)
                        # Пример: {"success": true} или {"message": "deleted"}
                        success = data.get("success")
                        message = data.get("message", "").lower()
                        assert success is True or "delete" in message or "удален" in message
                    except ValueError:
                        allure.attach(response.text, name="Non-JSON Response", attachment_type=AttachmentType.TEXT)

    with allure.step("Опциональная проверка: ресурс больше не должен существовать"):
        get_url = f"{base_url}/api/v1/resource_unit_measure/{unit_id}"
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
            allure.attach(
                "Ресурс успешно удалён и больше не доступен (404)",
                name="Проверка",
                attachment_type=AttachmentType.TEXT
            )
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
            f"Удалена единица измерения с ID={unit_id}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
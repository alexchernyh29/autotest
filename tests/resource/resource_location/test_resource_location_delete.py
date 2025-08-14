# Удаляет местоположение ресурса /api/v1/resource_location/{id}
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
    Получение токена аутентификации (как в предыдущих тестах)
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


@allure.story("Удаление местоположения ресурса по ID")
def test_delete_resource_location():
    """
    Тест: удаление существующего местоположения ресурса по ID
    Эндпоинт: DELETE /api/v1/resource_location/{id}
    Проверяет:
      - статус 200 или 204
      - отсутствие тела при 204
      - невозможность получить объект после удаления (опционально)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # ID местоположения для удаления
        location_id = os.getenv("RESOURCE_LOCATION_ID_TO_DELETE")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert location_id, "RESOURCE_LOCATION_ID_TO_DELETE не задан в .env"

    try:
        location_id = int(location_id)
        assert location_id > 0, "RESOURCE_LOCATION_ID_TO_DELETE должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_LOCATION_ID_TO_DELETE должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_location/{location_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка DELETE-запроса для удаления местоположения с ID={location_id}"):
        response = requests.delete(url, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 204:
            with allure.step("Успешно удалено (204 No Content)"):
                assert not response.text.strip(), "Ожидалось пустое тело при статусе 204"
        elif response.status_code == 200:
            with allure.step("Успешно удалено (200 OK)"):
                # Может вернуться подтверждение
                if response.text.strip():
                    try:
                        data = response.json()
                        allure.attach(str(data), name="Response JSON", attachment_type=AttachmentType.JSON)
                        # Проверяем, что удаление подтверждено
                        assert data.get("success") is True or data.get("deleted") is True or data.get("id") == location_id
                    except ValueError:
                        pass  # необязательно
        elif response.status_code == 404:
            pytest.fail(f"Местоположение с ID={location_id} уже не существует (404). Возможно, было удалено ранее.")
        elif response.status_code == 403:
            pytest.fail(f"Доступ запрещён (403). Проверьте права токена.")
        elif response.status_code != 200 and response.status_code != 204:
            pytest.fail(f"Ошибка: статус {response.status_code}, ответ: {response.text}")
        else:
            with allure.step("Местоположение успешно удалено"):
                pass

    # Опциональная проверка: попробуем получить местоположение после удаления
    with allure.step("Проверка, что местоположение действительно удалено (опционально)"):
        get_url = f"{base_url}/api/v1/resource_location/{location_id}"
        get_headers = {
            "accept": "application/json",
            "tockenid": token
        }
        verify_response = requests.get(get_url, headers=get_headers)

        if verify_response.status_code == 404:
            allure.attach(
                f"Подтверждено: местоположение с ID={location_id} больше не существует (404).",
                name="Проверка удаления",
                attachment_type=AttachmentType.TEXT
            )
        elif verify_response.status_code == 200:
            pytest.fail(f"Ошибка: местоположение с ID={location_id} всё ещё доступно после удаления!")
        else:
            allure.attach(
                f"Получен статус {verify_response.status_code} при проверке удаления.",
                name="Проверка удаления",
                attachment_type=AttachmentType.TEXT
            )

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Местоположение с ID={location_id} успешно удалено.",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
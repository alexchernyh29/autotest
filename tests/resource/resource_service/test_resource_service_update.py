# Обновляет информацию о существующем сервисе ресурсов /api/v1/resource_service/{id}
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
    return token_data.get("tockenID")  # Ожидается "tockenID" (с опечаткой)


@allure.story("Обновление сервиса ресурсов по ID (PUT)")
def test_update_resource_service_by_id():
    """
    Тест обновления сервиса ресурсов через PUT /api/v1/resource_service/{id}
    Проверяет:
    1. Успешный статус-код (200 или 201)
    2. Валидность JSON-ответа
    3. Наличие обязательных полей
    4. Соответствие обновлённых данных
    5. Неизменность ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        service_id = os.getenv("RESOURCE_SERVICE_ID", "12313213")  # Можно задать в .env

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert service_id, "RESOURCE_SERVICE_ID не задан"

    try:
        service_id = int(service_id)
        assert service_id > 0, "ID сервиса ресурсов должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_SERVICE_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    # Генерация новых уникальных значений
    import time
    updated_name = f"Обновлённое имя {int(time.time())}"
    updated_system_name = f"updated_sys_{int(time.time())}"

    with allure.step(f"Формирование тела запроса для обновления (ID={service_id})"):
        request_body = {
            "name": updated_name,
            "system_name": updated_system_name
        }
        allure.attach(str(request_body), name="Request Body (JSON)", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_service/{service_id}"
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка PUT-запроса на обновление сервиса ресурсов"):
        response = requests.put(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        # Обычно 200 или 201 при успешном обновлении
        assert response.status_code in [200, 201], (
            f"Ошибка при обновлении сервиса ресурсов. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        required_fields = ["id", "name", "system_name"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов
        assert isinstance(data["id"], int), "Поле 'id' должно быть числом"
        assert isinstance(data["name"], str), "Поле 'name' должно быть строкой"
        assert isinstance(data["system_name"], str), "Поле 'system_name' должно быть строкой"

        # Проверка соответствия ID
        assert data["id"] == service_id, (
            f"Ожидался ID={service_id}, но получен ID={data['id']}"
        )

        # Проверка, что данные обновились
        assert data["name"] == updated_name, f"Имя не обновилось: ожидается '{updated_name}', получено '{data['name']}'"
        assert data["system_name"] == updated_system_name, (
            f"System name не обновился: ожидается '{updated_system_name}', получено '{data['system_name']}'"
        )

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Сервис ресурсов успешно обновлён:\n"
            f"  ID: {data['id']}\n"
            f"  Name: {data['name']}\n"
            f"  System Name: {data['system_name']}",
            name="Результат обновления",
            attachment_type=AttachmentType.TEXT
        )
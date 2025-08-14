# Обновляет информацию о существующем пуле ресурсов /api/v1/resource_pool/{id}
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


@allure.story("Обновление информации о пуле ресурсов")
def test_update_resource_pool():
    """
    Тест: обновление существующего пула ресурсов по ID
    Эндпоинт: PUT /api/v1/resource_pool/{id}
    Поля: name, description, status_id, service_id, location_id, type_service_id
    Проверяет:
      - статус 200
      - валидный JSON в ответе
      - совпадение обновлённых полей
      - неизменность ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # ID пула для обновления
        pool_id = os.getenv("RESOURCE_POOL_ID_TO_UPDATE")

        # Новые значения
        name = os.getenv("UPDATE_POOL_NAME", "updated-pool-auto")
        description = os.getenv("UPDATE_POOL_DESCRIPTION", "Обновлённое описание пула")
        status_id = os.getenv("UPDATE_POOL_STATUS_ID", "1")
        service_id = os.getenv("UPDATE_POOL_SERVICE_ID", "1")
        location_id = os.getenv("UPDATE_POOL_LOCATION_ID", "2")
        type_service_id = os.getenv("UPDATE_POOL_TYPE_SERVICE_ID", "3")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert pool_id, "RESOURCE_POOL_ID_TO_UPDATE не задан в .env"
        assert name.strip(), "UPDATE_POOL_NAME не может быть пустым"

    # Приведение типов
    try:
        pool_id = int(pool_id)
        status_id = int(status_id)
        service_id = int(service_id)
        location_id = int(location_id)
        type_service_id = int(type_service_id)
    except (ValueError, TypeError) as e:
        pytest.fail(f"Ошибка преобразования числовых параметров: {e}")

    assert pool_id > 0, "RESOURCE_POOL_ID_TO_UPDATE должен быть положительным"
    assert status_id >= 0, "UPDATE_POOL_STATUS_ID должен быть >= 0"
    assert service_id > 0, "UPDATE_POOL_SERVICE_ID должен быть положительным"
    assert location_id > 0, "UPDATE_POOL_LOCATION_ID должен быть положительным"
    assert type_service_id > 0, "UPDATE_POOL_TYPE_SERVICE_ID должен быть положительным"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса (новые значения)"):
        payload = {
            "name": name,
            "description": description,
            "status_id": status_id,
            "service_id": service_id,
            "location_id": location_id,
            "type_service_id": type_service_id
        }
        allure.attach(str(payload), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_pool/{pool_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка PUT-запроса для обновления пула с ID={pool_id}"):
        response = requests.put(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Пул с ID={pool_id} не найден. Проверьте ID.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректные данные или ID. Ответ: {response.text}")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    with allure.step("Парсинг и валидация JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        required_fields = [
            "id", "name", "description", "status_id", "service_id",
            "location_id", "type_service_id", "created_at"
        ]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка ID
        assert isinstance(data["id"], int) and data["id"] == pool_id, f"ID в ответе ≠ {pool_id}"

        # Проверка обновлённых значений
        assert data["name"] == name, f"name: ожидаем '{name}', получено '{data['name']}'"
        assert data["description"] == description, "description не совпадает"
        assert data["status_id"] == status_id, "status_id не совпадает"
        assert data["service_id"] == service_id, "service_id не совпадает"
        assert data["location_id"] == location_id, "location_id не совпадает"
        assert data["type_service_id"] == type_service_id, "type_service_id не совпадает"

        # created_at — не должен меняться, но проверим формат
        assert isinstance(data["created_at"], str), "created_at должно быть строкой"
        assert "T" in data["created_at"] and "Z" in data["created_at"], "created_at должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Пул успешно обновлён: ID={data['id']}, Name='{data['name']}', "
            f"Service ID={data['service_id']}, Location ID={data['location_id']}, "
            f"Status ID={data['status_id']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
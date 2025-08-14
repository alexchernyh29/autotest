# Обновляет информацию о существующем местоположении ресурса /resource_location/{id}
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


@allure.story("Обновление информации о местоположении ресурса")
def test_update_resource_location():
    """
    Тест: обновление существующего местоположения ресурса по ID
    Эндпоинт: PUT /api/v1/resource_location/{id}
    Поля: name, address
    Проверяет:
      - статус 200
      - валидный JSON в ответе
      - совпадение обновлённых значений
      - неизменность ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # ID местоположения для обновления
        location_id = os.getenv("RESOURCE_LOCATION_ID_TO_UPDATE")

        # Новые значения
        name = os.getenv("UPDATE_LOCATION_NAME")
        address = os.getenv("UPDATE_LOCATION_ADDRESS", "")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert location_id, "RESOURCE_LOCATION_ID_TO_UPDATE не задан в .env"
        assert name and name.strip(), "UPDATE_LOCATION_NAME не задан или пуст"

    # Очистка значений
    name = name.strip()
    address = address.strip() if address else ""

    try:
        location_id = int(location_id)
        assert location_id > 0, "RESOURCE_LOCATION_ID_TO_UPDATE должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_LOCATION_ID_TO_UPDATE должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса (новые значения)"):
        payload = {
            "name": name,
            "address": address
        }
        allure.attach(str(payload), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_location/{location_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка PUT-запроса для обновления местоположения с ID={location_id}"):
        response = requests.put(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Местоположение с ID={location_id} не найдено. Проверьте ID.")
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

        required_fields = ["id", "name", "address", "status_id", "created_at"]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка ID
        assert isinstance(data["id"], int) and data["id"] == location_id, f"ID в ответе ≠ {location_id}"

        # Проверка обновлённых значений
        assert data["name"] == name, f"name: ожидаем '{name}', получено '{data['name']}'"
        assert data["address"] == address, f"address: ожидаем '{address}', получено '{data['address']}'"

        assert isinstance(data["status_id"], int), "status_id должно быть числом"
        assert data["status_id"] in [0, 1], "status_id должно быть 0 или 1"

        assert isinstance(data["created_at"], str), "created_at должно быть строкой"
        assert "T" in data["created_at"] and "Z" in data["created_at"], "created_at должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Местоположение успешно обновлено: ID={data['id']}, Name='{data['name']}', "
            f"Address='{data['address']}', Status ID={data['status_id']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
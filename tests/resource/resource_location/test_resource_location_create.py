# Создает новое местоположение ресурса /api/v1/resource_location
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


@allure.story("Создание нового местоположения ресурса")
def test_create_resource_location():
    """
    Тест: создание нового местоположения ресурса
    Эндпоинт: POST /api/v1/resource_location
    Поля: name, address
    Проверяет:
      - статус 200 или 201
      - валидный JSON в ответе
      - наличие ID и корректность полей
      - совпадение отправленных и полученных значений
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Параметры для создания местоположения
        name = os.getenv("LOCATION_NAME")
        address = os.getenv("LOCATION_ADDRESS", "")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert name and name.strip(), "LOCATION_NAME не задан или пуст в .env"

    # Обрезаем пробелы
    name = name.strip()
    address = address.strip() if address else ""

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса"):
        payload = {
            "name": name,
            "address": address
        }
        allure.attach(str(payload), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_location"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание местоположения"):
        response = requests.post(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code in [200, 201], (
            f"Ошибка при создании местоположения. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг и валидация JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        # Ожидаемые поля в ответе
        required_fields = ["id", "name", "address", "status_id", "created_at"]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка значений
        assert isinstance(data["id"], int) and data["id"] > 0, "ID должно быть положительным целым"
        assert data["name"] == name, f"Имя: ожидаем '{name}', получено '{data['name']}'"
        assert data["address"] == address, f"Адрес: ожидаем '{address}', получено '{data['address']}'"
        assert isinstance(data["status_id"], int), "status_id должно быть числом"
        assert data["status_id"] in [0, 1], "status_id должно быть 0 (неактивно) или 1 (активно)"

        assert isinstance(data["created_at"], str), "created_at должно быть строкой"
        assert "T" in data["created_at"] and "Z" in data["created_at"], "created_at должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Местоположение успешно создано: ID={data['id']}, Name='{data['name']}', "
            f"Address='{data['address']}', Status ID={data['status_id']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
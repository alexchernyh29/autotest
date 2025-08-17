# Создает новую единицу измерения ресурсов /api/v1/resource_units_measure
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


@allure.story("Создание единицы измерения ресурса")
def test_create_resource_unit_measure():
    """
    Тест создания новой единицы измерения через POST /api/v1/resource_units_measure
    Проверяет:
    1. Успешный статус-код (200 или 201)
    2. Валидность JSON-ответа
    3. Наличие ID и переданных данных в ответе
    4. Корректность типов полей
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    # Генерация уникального имени, чтобы избежать конфликтов
    import time
    unique_name = f"Ед. изм. {int(time.time())}"

    with allure.step("Формирование тела запроса"):
        request_body = {
            "name": unique_name
        }
        allure.attach(str(request_body), name="Request Body (JSON)", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_units_measure"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание единицы измерения"):
        response = requests.post(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        # Обычно 200 или 201 при успешном создании
        assert response.status_code in [200, 201], (
            f"Ошибка при создании единицы измерения. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        required_fields = ["id", "name"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"В ответе отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов
        assert isinstance(data["id"], int), "Поле 'id' должно быть числом"
        assert isinstance(data["name"], str), "Поле 'name' должно быть строкой"
        assert data["id"] > 0, "ID должен быть положительным"
        assert data["name"] == request_body["name"], "Имя в ответе не совпадает с отправленным"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Создана единица измерения: ID={data['id']}, Name='{data['name']}'",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
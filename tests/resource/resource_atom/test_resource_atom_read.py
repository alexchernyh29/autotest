# Получение информации об атоме ресурса /api/v1/resource_atom/{id}
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


@allure.story("Получение атомарного ресурса по ID")
def test_get_resource_atom_by_id():
    """
    Тест получения атомарного ресурса по его ID
    Проверяет:
    1. Успешный статус-код (200)
    2. Валидность JSON-ответа
    3. Наличие обязательных полей
    4. Корректность типа данных
    5. Соответствие запрошенному ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        resource_atom_id = os.getenv("RESOURCE_ATOM_ID", "1")  # Можно задать в .env или использовать по умолчанию

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert resource_atom_id, "RESOURCE_ATOM_ID не задан и отсутствует fallback"

    try:
        resource_atom_id = int(resource_atom_id)
        assert resource_atom_id > 0, "ID ресурса должно быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_ATOM_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для получения resource_atom с ID={resource_atom_id}"):
        url = f"{base_url}/api/v1/resource_atom/{resource_atom_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка GET-запроса"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Ресурс с ID={resource_atom_id} не найден. Проверьте корректность ID.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный запрос. Возможно, ID имеет неверный формат.")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка API: статус {response.status_code}, тело: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        required_fields = ["id", "category_id", "name", "description"]
        missing_fields = [field for field in required_fields if field not in data]

        assert not missing_fields, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"

        # Проверка типа данных
        assert isinstance(data["id"], int), "Поле 'id' должно быть числом"
        assert isinstance(data["category_id"], int), "category_id должно быть числом"
        assert isinstance(data["name"], str), "name должно быть строкой"
        assert isinstance(data["description"], str), "description должно быть строкой"

        # Проверка соответствия ID
        assert data["id"] == resource_atom_id, (
            f"Ожидался ресурс с ID={resource_atom_id}, но получен ID={data['id']}"
        )

    with allure.step("Тест пройден успешно"):
        allure.attach(
            f"Успешно получен resource_atom: ID={data['id']}, Name='{data['name']}'", 
            name="Результат", 
            attachment_type=AttachmentType.TEXT
        )
# Обновляет информацию об атоме ресурса /api/v1/resource_atom/{id}
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


@allure.story("Обновление атомарного ресурса по ID (PUT)")
def test_update_resource_atom_by_id():
    """
    Тест обновления атомарного ресурса через PUT /api/v1/resource_atom/{id}
    Проверяет:
    1. Успешный статус-код (200 или 201)
    2. Валидность JSON-ответа
    3. Наличие обязательных полей
    4. Соответствие обновлённых данных отправленным
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        resource_atom_id = os.getenv("RESOURCE_ATOM_ID", "1")  # Можно задать в .env

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

    with allure.step(f"Формирование тела запроса для обновления resource_atom (ID={resource_atom_id})"):
        request_body = {
            "category_id": 1,
            "name": "Обновлённое имя ресурса",
            "description": "Обновлённое описание ресурса"
        }
        allure.attach(str(request_body), name="Request Body (JSON)", attachment_type=AttachmentType.JSON)

    with allure.step(f"Формирование URL и заголовков для PUT-запроса"):
        url = f"{base_url}/api/v1/resource_atom/{resource_atom_id}"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка PUT-запроса на обновление ресурса"):
        response = requests.put(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        # Обычно при обновлении — 200 OK, иногда 201
        assert response.status_code in [200, 201], (
            f"Ошибка при обновлении resource_atom. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

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
            f"Ожидался ID={resource_atom_id}, но получен ID={data['id']}"
        )

        # Проверка, что данные обновились
        assert data["name"] == request_body["name"], "Имя не обновилось или не совпадает"
        assert data["description"] == request_body["description"], "Описание не обновилось"
        assert data["category_id"] == request_body["category_id"], "category_id не обновился"

    with allure.step("Ресурс успешно обновлён"):
        allure.attach(
            f"Обновлён resource_atom ID={data['id']}:\n"
            f"  Name: {data['name']}\n"
            f"  Description: {data['description']}\n"
            f"  Category ID: {data['category_id']}",
            name="Результат обновления",
            attachment_type=AttachmentType.TEXT
        )
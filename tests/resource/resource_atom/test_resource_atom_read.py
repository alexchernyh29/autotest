import os
import pytest
import requests
import allure
from dotenv import load_dotenv, find_dotenv
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
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


@allure.story("Получение атомарного ресурса по ID")
def test_get_resource_atom_by_id():
    """
    Тест получения атомарного ресурса по ID.
    Проверяет:
    1. Статус 200
    2. Валидность JSON
    3. Наличие и тип всех обязательных полей (включая вложенные)
    4. Соответствие запрошенному ID
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

    with allure.step(f"Формирование URL для GET /resource_atom/{resource_atom_id}"):
        url = f"{base_url}/api/v1/resource_atom/{resource_atom_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

    with allure.step("Отправка GET-запроса"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Ресурс с ID={resource_atom_id} не найден.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный ID формата. Ответ: {response.text}")
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), "Parsed Response", AttachmentType.JSON)

    with allure.step("Проверка обязательных полей и типов"):
        # Основные поля
        required_top_level = ["id", "name", "description", "category", "create_time", "update_time", "create_user_id", "update_user_id"]
        missing = [field for field in required_top_level if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов верхнего уровня
        assert isinstance(data["id"], int), "'id' должно быть числом"
        assert isinstance(data["name"], str), "'name' должно быть строкой"
        assert isinstance(data["description"], str), "'description' должно быть строкой"
        assert isinstance(data["create_user_id"], int), "'create_user_id' должно быть числом"
        assert isinstance(data["update_user_id"], int), "'update_user_id' должно быть числом"

        # Проверка вложенного объекта 'category'
        assert isinstance(data["category"], dict), "'category' должно быть объектом"
        assert "id" in data["category"], "В 'category' отсутствует 'id'"
        assert isinstance(data["category"]["id"], int), "'category.id' должно быть числом"
        assert data["category"]["id"] > 0, "'category.id' должно быть положительным"

        # Проверка времени (упрощённо)
        for time_field in ["create_time", "update_time"]:
            assert isinstance(data[time_field], dict), f"'{time_field}' должно быть объектом"
            assert "date" in data[time_field], f"'{time_field}.date' отсутствует"
            assert isinstance(data[time_field]["date"], str), f"'{time_field}.date' должно быть строкой"
            assert "timezone" in data[time_field], f"'{time_field}.timezone' отсутствует"

        # Проверка соответствия ID
        assert data["id"] == resource_atom_id, (
            f"Ожидался ID={resource_atom_id}, получен ID={data['id']}"
        )

    with allure.step("Тест успешно пройден"):
        allure.attach(
            f"Получен ресурс: ID={data['id']}, Name='{data['name']}', Category ID={data['category']['id']}",
            "Результат",
            AttachmentType.TEXT
        )
# Возвращает информацию о единице измерения ресурсов /api/v1/resource_unit_measure/{id}
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
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    response.raise_for_status()
    token_data = response.json()
    return token_data.get("tockenID")


# Список тестовых данных: id → ожидаемое имя
TEST_DATA = [
    {"id": 67, "name": "Час"},
    {"id": 4, "name": "Гбайт"},
    {"id": 61, "name": "Шт"},
    {"id": 71, "name": "Мбит/с"}
]


@allure.story("Получение единицы измерения по ID")
@pytest.mark.parametrize("unit_data", TEST_DATA, ids=[f"ID={d['id']}" for d in TEST_DATA])
def test_get_resource_unit_measure_by_id(unit_data):
    """
    Параметризованный тест получения единицы измерения по ID.
    Проверяет:
    1. Успешный статус (200)
    2. Корректность ID и имени в ответе
    3. Валидность JSON
    4. Структуру ответа
    """
    unit_id = unit_data["id"]
    expected_name = unit_data["name"]

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

    with allure.step(f"Формирование URL для получения единицы измерения (ID={unit_id})"):
        url = f"{base_url}/api/v1/resource_unit_measure/{unit_id}"
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
            pytest.fail(f"Единица измерения с ID={unit_id} не найдена. Возможно, справочник изменился.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный ID: {unit_id}. Ответ сервера: {response.text}")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка API: статус {response.status_code}, тело: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры и содержимого ответа"):
        required_fields = ["id", "name"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов
        assert isinstance(data["id"], int), "Поле 'id' должно быть целым числом"
        assert isinstance(data["name"], str), "Поле 'name' должно быть строкой"

        # Проверка значений
        assert data["id"] == unit_id, (
            f"Ожидался ID={unit_id}, но получен ID={data['id']}"
        )
        assert data["name"] == expected_name, (
            f"Ожидалось имя '{expected_name}', но получено '{data['name']}'"
        )

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Успешно получена единица измерения:\n"
            f"  ID: {data['id']}\n"
            f"  Name: {data['name']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
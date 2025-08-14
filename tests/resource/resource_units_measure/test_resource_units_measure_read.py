# Возвращает информацию о единице измерения ресурсов /api/v1/resource_unit_measure/{id}
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


@allure.story("Получение единицы измерения по ID")
def test_get_resource_unit_measure_by_id():
    """
    Тест получения единицы измерения ресурса по ID
    Проверяет:
    1. Успешный статус-код (200)
    2. Валидность JSON-ответа
    3. Наличие обязательных полей
    4. Соответствие ID в URL и в ответе
    5. Корректность типов данных
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        unit_id = os.getenv("RESOURCE_UNIT_MEASURE_ID", "1231231")  # Можно задать в .env

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert unit_id, "RESOURCE_UNIT_MEASURE_ID не задан"

    try:
        unit_id = int(unit_id)
        assert unit_id > 0, "ID единицы измерения должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_UNIT_MEASURE_ID должен быть целым положительным числом")

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
            pytest.fail(f"Единица измерения с ID={unit_id} не найдена. Проверьте корректность ID.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный формат ID. Возможно, передано не число.")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка API: статус {response.status_code}, тело: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        required_fields = ["id", "name"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов
        assert isinstance(data["id"], int), "Поле 'id' должно быть числом"
        assert isinstance(data["name"], str), "Поле 'name' должно быть строкой"

        # Проверка соответствия ID
        assert data["id"] == unit_id, (
            f"Ожидалась единица измерения с ID={unit_id}, но получен ID={data['id']}"
        )

        # Проверка, что имя не пустое
        assert data["name"].strip() != "", "Поле 'name' не должно быть пустым"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Получена единица измерения:\n"
            f"  ID: {data['id']}\n"
            f"  Name: {data['name']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
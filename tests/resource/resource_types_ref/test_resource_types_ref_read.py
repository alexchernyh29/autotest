# Возвращает список всех типов ресурсов (справочник) /api/v1/resource_types_ref
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
    return token_data.get("tockenID")  # Ожидаем поле "tockenID" (с опечаткой)


@allure.story("Получение справочника типов ресурсов (resource_types_ref)")
def test_get_resource_types_ref():
    """
    Тест получения списка всех типов ресурсов (справочник)
    Проверяет:
    1. Успешный статус-код (200)
    2. Ответ в формате JSON
    3. Наличие массива данных
    4. Структуру каждого элемента (id, name, code)
    5. Непустой ответ (если ожидается)
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

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_types_ref"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка GET-запроса к /resource_types_ref"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении справочника типов ресурсов. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        assert isinstance(data, list), "Ожидался массив типов ресурсов"

    if len(data) == 0:
        with allure.step("Внимание: справочник пуст"):
            allure.attach(
                "Список типов ресурсов пуст. Проверьте, заполнены ли данные в системе.",
                name="Предупреждение",
                attachment_type=AttachmentType.TEXT
            )
    else:
        with allure.step("Проверка структуры каждого элемента"):
            required_fields = ["id", "name", "code"]
            for idx, item in enumerate(data):
                assert isinstance(item, dict), f"Элемент [{idx}] не является объектом"

                missing = [field for field in required_fields if field not in item]
                assert not missing, f"В элементе [{idx}] отсутствуют поля: {', '.join(missing)}"

                # Проверка типов
                assert isinstance(item["id"], int), f"id элемента [{idx}] должно быть числом"
                assert isinstance(item["name"], str), f"name элемента [{idx}] должно быть строкой"
                assert isinstance(item["code"], str), f"code элемента [{idx}] должно быть строкой"

                # Проверка, что строки не пустые
                assert item["name"].strip() != "", f"name элемента [{idx}] не должен быть пустым"
                assert item["code"].strip() != "", f"code элемента [{idx}] не должен быть пустым"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Получено {len(data)} типов ресурсов",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
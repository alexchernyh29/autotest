# tests/resource/test_get_resource_types_ref.py

import os
import pytest
import json
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
    return token_data.get("tockenID")  # Обратите внимание на опечатку: tockenID


@allure.story("Получение справочника типов ресурсов (resource_types_ref)")
def test_get_resource_types_ref():
    """
    Тест получения списка всех типов ресурсов (справочник)
    Проверяет:
    1. Успешный статус-код (200)
    2. Ответ в формате JSON
    3. Наличие массива данных
    4. Структуру каждого элемента (id, name)
    5. Непустой ответ
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
        allure.attach(
            json.dumps(headers, ensure_ascii=False, indent=2),
            name="Request Headers",
            attachment_type=AttachmentType.JSON
        )

    with allure.step("Отправка GET-запроса к /resource_types_ref"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(
            json.dumps(dict(response.headers), ensure_ascii=False, indent=2),
            name="Response Headers",
            attachment_type=AttachmentType.JSON
        )

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

        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name="Parsed Response Data",
            attachment_type=AttachmentType.JSON
        )

        assert isinstance(data, list), "Ожидался массив типов ресурсов"

    with allure.step("Проверка: список не должен быть пустым"):
        assert len(data) > 0, "Список типов ресурсов пуст — ожидался хотя бы один элемент"

    with allure.step(f"Проверка структуры {len(data)} элементов"):
        required_fields = ["id", "name"]  # Поле 'code' отсутствует в ответе

        for idx, item in enumerate(data):
            with allure.step(f"Тип ресурса #{idx + 1} (ID={item.get('id')})"):
                assert isinstance(item, dict), "Каждый элемент должен быть объектом"

                missing = [field for field in required_fields if field not in item]
                assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

                # Проверка типов
                assert isinstance(item["id"], int), "Поле 'id' должно быть целым числом"
                assert isinstance(item["name"], str), "Поле 'name' должно быть строкой"

                # Проверка, что имя не пустое
                assert item["name"].strip() != "", "Поле 'name' не должно быть пустым"

    with allure.step("✅ Тест завершён успешно"):
        names = [item["name"] for item in data]
        allure.attach(
            f"Получены типы ресурсов: {', '.join(names)}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
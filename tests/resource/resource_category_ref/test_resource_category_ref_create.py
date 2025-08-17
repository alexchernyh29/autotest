# test_create_resource_category_ref.py

import os
import random
import pytest
import requests
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = Path(find_dotenv())
assert ENV_FILE.exists(), "Файл .env не найден в корне проекта"


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
        allure.attach(f"URL: {url}", "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)
        allure.attach(str(params), "Request Params", AttachmentType.JSON)

        response = requests.post(url, headers=headers, params=params)
        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


def set_env_variable(key: str, value: str, env_path: Path):
    """
    Обновляет или добавляет переменную в .env
    """
    lines = []
    key_found = False

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

    with open(env_path, "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip().startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                key_found = True
            else:
                file.write(line)
        if not key_found:
            file.write(f"{key}={value}\n")

    os.environ[key] = value


@allure.story("Создание категории ресурса (resource_category_ref)")
def test_create_resource_category_ref():
    """
    Тест: создание новой категории ресурса с рандомными полями
    - Поля: type_ref_id, unit_measure_id, category_type_id — случайные из списков
    - Ответ ожидается: {"id": N}
    - Сохраняет ID в RESOURCE_CATEGORY_REF_ID
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

    # Рандомные значения
    type_ref_id = random.choice([1, 3])
    unit_measure_id = random.choice([71, 67, 61, 4])
    category_type_id = random.choice([11, 10, 9, 8, 7, 6, 3, 2, 1])

    # Генерация имени
    name = f"Категория автотест {type_ref_id}_{unit_measure_id}_{category_type_id}"

    with allure.step("Формирование тела запроса с рандомными значениями"):
        payload = {
            "type_ref_id": type_ref_id,
            "unit_measure_id": unit_measure_id,
            "name": name,
            "category_type_id": category_type_id
        }
        allure.attach(str(payload), "Request Body", AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_category_ref"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

    with allure.step("Отправка POST-запроса"):
        response = requests.post(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text or "null", "Response Body", AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"Тело: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), "Parsed Response", AttachmentType.JSON)

    with allure.step("Проверка структуры ответа: {\"id\": N}"):
        assert isinstance(data, dict), "Ожидался объект в формате {\"id\": N}"
        assert "id" in data, "В ответе отсутствует поле 'id'"
        assert isinstance(data["id"], int), "'id' должно быть целым числом"
        assert data["id"] > 0, "'id' должно быть положительным"

    created_id = data["id"]

    with allure.step(f"Сохранение RESOURCE_CATEGORY_REF_ID={created_id} в .env"):
        set_env_variable("RESOURCE_CATEGORY_REF_ID", str(created_id), ENV_FILE)
        allure.attach(
            f"ID {created_id} сохранён в .env как RESOURCE_CATEGORY_REF_ID",
            "Сохранение ID",
            AttachmentType.TEXT
        )

    with allure.step("Тест успешно пройден"):
        allure.attach(
            f"Создана категория ресурса: ID={created_id}, Name='{name}'",
            "Результат",
            AttachmentType.TEXT
        )
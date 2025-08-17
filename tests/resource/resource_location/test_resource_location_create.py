# test_create_resource_location.py

import os
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
        allure.attach(f"URL: {url}", name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(params), name="Request Params", attachment_type=AttachmentType.TEXT)

        response = requests.post(url, headers=headers, params=params)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


def set_env_variable(key: str, value: str, env_path: Path):
    """
    Обновляет или добавляет переменную в .env файл
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

    # Обновляем текущую сессию
    os.environ[key] = value


@allure.story("Создание нового местоположения ресурса")
def test_create_resource_location():
    """
    Тест: создание нового местоположения ресурса
    - Использует фиксированные данные: "Облако автотеста", "РФ, Москва"
    - Проверяет статус 200
    - Проверяет наличие id
    - Сохраняет id в переменную RESOURCE_LOCATION_ID
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

    # Фиксированные данные для создания
    payload = {
        "name": "Облако автотеста",
        "address": "РФ, Москва"
    }

    with allure.step("Формирование тела запроса"):
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

    with allure.step("Проверка статуса ответа (ожидается 200)"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка наличия и корректности поля 'id'"):
        assert "id" in data, "В ответе отсутствует 'id'"
        assert isinstance(data["id"], int), "'id' должно быть целым числом"
        assert data["id"] > 0, "'id' должно быть положительным"

        location_id = data["id"]

    with allure.step(f"Сохранение RESOURCE_LOCATION_ID={location_id} в .env"):
        set_env_variable("RESOURCE_LOCATION_ID", str(location_id), ENV_FILE)
        allure.attach(
            f"ID {location_id} сохранён в {ENV_FILE} как RESOURCE_LOCATION_ID",
            name="Сохранение ID",
            attachment_type=AttachmentType.TEXT
        )

    with allure.step("Тест успешно пройден"):
        allure.attach(
            f"Создано местоположение: ID={location_id}, Name='{payload['name']}', Address='{payload['address']}'",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
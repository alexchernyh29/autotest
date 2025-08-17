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


@allure.story("Создание атомарного ресурса (resource_atom)")
def test_create_resource_atom():
    """
    Тест создания нового атомарного ресурса.
    После успешного создания:
    - Сохраняет ID в .env как RESOURCE_ATOM_ID
    - Обновляет текущую сессию
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

    with allure.step("Формирование тела запроса для создания resource_atom"):
        request_body = {
            "category_id": 261,
            "name": "Тестовый ресурс ",
            "description": "Описание созданного тестового атомарного ресурса"
        }
        allure.attach(str(request_body), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_atom"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание resource_atom"):
        response = requests.post(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code in [200, 201], (
            f"Ошибка при создании resource_atom. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка наличия и типа поля 'id'"):
        assert "id" in data, "В ответе отсутствует 'id'"
        assert isinstance(data["id"], int), "'id' должен быть целым числом"
        assert data["id"] > 0, "'id' должен быть положительным"

    created_id = data["id"]

    with allure.step(f"Сохранение RESOURCE_ATOM_ID={created_id} в .env"):
        set_env_variable("RESOURCE_ATOM_ID", str(created_id), ENV_FILE)
        allure.attach(
            f"ID {created_id} успешно сохранён в {ENV_FILE} как RESOURCE_ATOM_ID",
            name="Сохранение ID",
            attachment_type=AttachmentType.TEXT
        )

    with allure.step("Тест успешно пройден: ресурс создан и ID сохранён"):
        allure.attach(f"Создан resource_atom с ID: {created_id}", name="Результат", attachment_type=AttachmentType.TEXT)
# Создает новый сервис ресурсов /api/v1/resource_service
import os
import pytest
import requests
import allure
import json
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
        allure.attach(json.dumps(headers, indent=2, ensure_ascii=False),
                      name="Request Headers", attachment_type=AttachmentType.JSON)
        allure.attach(json.dumps(params, indent=2, ensure_ascii=False),
                      name="Request Params", attachment_type=AttachmentType.JSON)

        response = requests.post(url, headers=headers, params=params)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(dict(response.headers)), name="Response Headers", attachment_type=AttachmentType.JSON)
        allure.attach(response.text, name="Response Body", attachment_type=AttachmentType.TEXT)

        response.raise_for_status()
        token_data = response.json()
        token = token_data.get("tockenID")
        assert token, "Ключ 'tockenID' отсутствует в ответе"
        return token


def write_env_var(key: str, value: str, env_file: str = ".env"):
    """Обновляет или добавляет переменную в .env файл"""
    from pathlib import Path

    env_path = Path(env_file)
    lines = []

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

    with open(env_path, "w", encoding="utf-8") as file:
        var_set = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                var_set = True
            else:
                file.write(line)
        if not var_set:
            file.write(f"{key}={value}\n")


@allure.story("Создание нового сервиса ресурсов")
def test_create_resource_service():
    """
    Тест: создание нового сервиса ресурсов
    Эндпоинт: POST /api/v1/resource_service
    Поля: name, sys_name
    Проверяет:
      - успешный статус (200 или 201)
      - валидный JSON с ID
      - сохранение ID в .env для последующих тестов
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Генерируем уникальные значения, если не заданы
        import time
        timestamp = int(time.time())
        name = os.getenv("SERVICE_NAME", f"Тестовый сервис {timestamp}")
        sys_name = os.getenv("SERVICE_SYS_NAME", f"test_service_{timestamp}")  # Уникальный!

        # Убираем лишние пробелы
        name = name.strip()
        sys_name = sys_name.strip()

        # Логируем значения
        env_values = {
            "API_URL": base_url,
            "API_LOGIN": login,
            "API_PASSWORD": "***" if password else None,
            "API_DOMAIN": domain,
            "SERVICE_NAME": name,
            "SERVICE_SYS_NAME": sys_name
        }
        allure.attach(
            json.dumps(env_values, indent=2, ensure_ascii=False),
            name="Значения из .env",
            attachment_type=AttachmentType.JSON
        )

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert name, "SERVICE_NAME не может быть пустым"
        assert sys_name, "SERVICE_SYS_NAME не может быть пустым"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"
        allure.attach(token, name="Authentication Token", attachment_type=AttachmentType.TEXT)

    with allure.step("Формирование тела запроса"):
        payload = {
            "name": name,
            "system_name": sys_name
        }
        # Защита от отсутствия поля
        assert "system_name" in payload and payload["system_name"], "Поле system_name отсутствует или пустое"
        allure.attach(
            json.dumps(payload, indent=2, ensure_ascii=False),
            name="Request Body",
            attachment_type=AttachmentType.JSON
        )

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_service"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(
            json.dumps(headers, indent=2, ensure_ascii=False),
            name="Request Headers",
            attachment_type=AttachmentType.JSON
        )

    with allure.step("Отправка POST-запроса на создание сервиса"):
        response = requests.post(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(response.text, name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(
            json.dumps(dict(response.headers), indent=2, ensure_ascii=False),
            name="Response Headers",
            attachment_type=AttachmentType.JSON
        )

    with allure.step("Проверка статуса ответа"):
        assert response.status_code in [200, 201], (
            f"Ошибка при создании сервиса. Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг и валидация JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail(f"Ответ не является валидным JSON: {response.text}")

        allure.attach(
            json.dumps(data, indent=2, ensure_ascii=False),
            name="Parsed Response Data",
            attachment_type=AttachmentType.JSON
        )

        assert isinstance(data, dict), "Ожидался объект в ответе"
        assert "id" in data, "В ответе отсутствует поле 'id'"
        assert isinstance(data["id"], int) and data["id"] > 0, "ID должен быть положительным целым числом"

        created_id = data["id"]

    with allure.step(f"Сохранение ID={created_id} в .env как LAST_CREATED_SERVICE_ID"):
        write_env_var("LAST_CREATED_SERVICE_ID", str(created_id), env_file=ENV_FILE)
        allure.attach(
            f"Сохранено: LAST_CREATED_SERVICE_ID={created_id}",
            name="Сохранение ID",
            attachment_type=AttachmentType.TEXT
        )

    with allure.step("Тест завершён успешно"):
        result_msg = (
            f"Сервис ресурсов успешно создан:\n"
            f"ID = {created_id}\n"
            f"Name = '{name}'\n"
            f"SysName = '{sys_name}'"
        )
        allure.attach(result_msg, name="Результат", attachment_type=AttachmentType.TEXT)
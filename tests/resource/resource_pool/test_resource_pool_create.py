# Создает новый пул ресурсов /api/v1/resource_pool
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
    return token_data.get("tockenID")


def write_env_var(key: str, value: str, env_file: str = ".env"):
    """
    Обновляет или добавляет переменную в .env файл
    """
    env_path = Path(env_file)
    lines = []

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

    with open(env_path, "w", encoding="utf-8") as file:
        var_set = False
        for line in lines:
            # Пропускаем пустые строки и комментарии
            stripped = line.strip()
            if stripped.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                var_set = True
            else:
                file.write(line)
        if not var_set:
            file.write(f"{key}={value}\n")


@allure.story("Создание нового пула ресурсов")
def test_create_resource_pool():
    """
    Тест: создание нового пула ресурсов
    Эндпоинт: POST /api/v1/resource_pool
    Поля: name, description, status_id, service_id, location_id, type_service_id
    Ожидаемый ответ: {"id": <int>}
    Сохраняет ID в .env как POOL_ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Параметры для создания пула
        name = os.getenv("POOL_NAME", "Тестовый пул ресурсов")
        description = os.getenv("POOL_DESCRIPTION", "Тестовый пул ресурсов")
        status_id = os.getenv("POOL_STATUS_ID", "2")
        service_id = os.getenv("POOL_SERVICE_ID", "414")
        location_id = os.getenv("POOL_LOCATION_ID", "125")
        type_service_id = os.getenv("POOL_TYPE_SERVICE_ID", "1")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert name.strip(), "POOL_NAME не может быть пустым"

    # Приведение типов
    try:
        status_id = int(status_id)
        service_id = int(service_id)
        location_id = int(location_id)
        type_service_id = int(type_service_id)
    except (ValueError, TypeError) as e:
        pytest.fail(f"Ошибка преобразования числовых параметров: {e}")

    assert status_id >= 0, "status_id должен быть >= 0"
    assert service_id > 0, "service_id должен быть положительным"
    assert location_id > 0, "location_id должен быть положительным"
    assert type_service_id > 0, "type_service_id должен быть положительным"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса"):
        payload = {
            "name": name,
            "description": description,
            "status_id": status_id,
            "service_id": service_id,
            "location_id": location_id,
            "type_service_id": type_service_id
        }
        allure.attach(str(payload), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_pool"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание пула ресурсов"):
        response = requests.post(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code in [200, 201], (
            f"Ошибка при создании пула ресурсов. Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг и валидация JSON-ответа (ожидается только ID)"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        assert isinstance(data, dict), "Ожидался объект в ответе"
        assert "id" in data, "В ответе отсутствует поле 'id'"

        created_id = data["id"]
        assert isinstance(created_id, int), "Поле 'id' должно быть целым числом"
        assert created_id > 0, "Поле 'id' должно быть положительным"

    with allure.step(f"Сохранение ID={created_id} в .env файл"):
        write_env_var("POOL_ID", str(created_id), env_file=ENV_FILE)
        allure.attach(
            f"Сохранено в .env: POOL_ID='{created_id}'",
            name="Сохранение ID",
            attachment_type=AttachmentType.TEXT
        )

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Пул ресурсов успешно создан. Присвоен ID: {created_id}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
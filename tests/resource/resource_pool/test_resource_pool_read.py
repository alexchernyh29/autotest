# Возвращает информацию о пуле ресурсов /api/v1/resource_pool/{id}
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


@allure.story("Получение информации о пуле ресурсов по ID")
def test_get_resource_pool_by_id():
    """
    Тест: получение данных о пуле ресурсов по ID
    Эндпоинт: GET /api/v1/resource_pool/{id}
    Проверяет:
      - статус 200
      - валидный JSON
      - наличие и корректность всех вложенных полей
      - соответствие ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        pool_id = os.getenv("POOL_ID")  # может быть из предыдущего теста

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert pool_id, "POOL_ID не задан в .env"

    try:
        pool_id = int(pool_id)
        assert pool_id > 0, "POOL_ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("POOL_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для получения пула с ID={pool_id}"):
        url = f"{base_url}/api/v1/resource_pool/{pool_id}"
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
            pytest.fail(f"Пул с ID={pool_id} не найден. Возможно, он был удалён или не создан.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный ID: {pool_id}. Ответ: {response.text}")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка сервера: статус {response.status_code}, ответ: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

    with allure.step("Валидация структуры и значений ответа"):
        # Проверка корневых полей
        required_root_fields = ["id", "name", "description", "service_id", "location", "status", "type_service", "create_time", "update_time"]
        missing = [field for field in required_root_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка ID
        assert isinstance(data["id"], int), "id должно быть целым числом"
        assert data["id"] == pool_id, f"Ожидался ID={pool_id}, получено {data['id']}"

        # name и description
        assert isinstance(data["name"], str) and data["name"], "name должно быть непустой строкой"
        assert isinstance(data["description"], str), "description должно быть строкой"

        # service_id
        assert isinstance(data["service_id"], int) and data["service_id"] > 0, "service_id должно быть положительным целым"

        # location (объект)
        assert isinstance(data["location"], dict), "location должно быть объектом"
        loc = data["location"]
        assert "id" in loc and loc["id"] == data["location_id"] if "location_id" in data else True
        assert isinstance(loc["id"], int) and loc["id"] > 0, "location.id должно быть положительным"
        assert isinstance(loc["name"], str) and loc["name"], "location.name должно быть непустой строкой"
        assert "address" in loc and isinstance(loc["address"], str), "location.address должно быть строкой"

        # status (объект)
        assert isinstance(data["status"], dict), "status должно быть объектом"
        status = data["status"]
        assert isinstance(status["id"], int) and status["id"] > 0, "status.id должно быть положительным"
        assert isinstance(status["sys_name"], str), "status.sys_name должно быть строкой"
        assert isinstance(status["name"], str), "status.name должно быть строкой"

        # type_service (объект)
        assert isinstance(data["type_service"], dict), "type_service должно быть объектом"
        tsvc = data["type_service"]
        assert isinstance(tsvc["id"], int) and tsvc["id"] > 0, "type_service.id должно быть положительным"
        assert isinstance(tsvc["sys_name"], str), "type_service.sys_name должно быть строкой"
        assert isinstance(tsvc["name"], str), "type_service.name должно быть строкой"

        # create_time и update_time (объекты с вложенной структурой)
        for time_field in ["create_time", "update_time"]:
            assert time_field in data, f"Отсутствует поле {time_field}"
            time_obj = data[time_field]
            assert isinstance(time_obj, dict), f"{time_field} должно быть объектом"
            assert "date" in time_obj and isinstance(time_obj["date"], str), f"{time_field}.date должно быть строкой"
            assert "timezone_type" in time_obj and isinstance(time_obj["timezone_type"], int)
            assert "timezone" in time_obj and isinstance(time_obj["timezone"], str)

        # create_user_id, update_user_id
        assert isinstance(data["create_user_id"], int) and data["create_user_id"] > 0
        assert isinstance(data["update_user_id"], int) and data["update_user_id"] > 0

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Успешно получен пул ресурсов: ID={data['id']}, Name='{data['name']}', "
            f"Service ID={data['service_id']}, Location='{data['location']['name']}', "
            f"Status='{data['status']['name']}', Type='{data['type_service']['name']}'",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
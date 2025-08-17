# Возвращает информацию о связи пула ресурсов и атома /api/v1/resource_pool_link_atom/{id}
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
    Получение токена аутентификации (как в предыдущих тестах)
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


@allure.story("Получение информации о связи пула ресурсов и атома по ID")
def test_get_resource_pool_atom_link_by_id():
    """
    Тест: получение данных о связи по ID
    Эндпоинт: GET /api/v1/resource_pool_link_atom/{id}
    Проверяет:
      - статус 200
      - валидный JSON
      - наличие и корректность полей
      - соответствие ожидаемым данным (если заданы в .env)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # ID связи для запроса
        link_id = os.getenv("RESOURCE_POOL_LINK_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert link_id, "RESOURCE_POOL_LINK_ID не задан в .env"

    try:
        link_id = int(link_id)
        assert link_id > 0, "RESOURCE_POOL_LINK_ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_POOL_LINK_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование URL"):
        url = f"{base_url}/api/v1/resource_pool_link_atom/{link_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }

        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка GET-запроса для получения связи с ID={link_id}"):
        response = requests.get(url, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Связь с ID={link_id} не найдена. Проверьте корректность ID.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный ID: {link_id}. Ответ: {response.text}")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        # Ожидаемые поля (адаптированы из предыдущего теста создания)
        required_fields = [
            "id", "pool_id", "atom_id", "min_count", "max_count",
            "cost_price_active", "cost_price_passive", "type_use", "created_at"
        ]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов и значений
        assert isinstance(data["id"], int) and data["id"] > 0, "ID должен быть положительным целым"
        assert data["id"] == link_id, f"Вернулся ID={data['id']}, ожидался {link_id}"

        assert isinstance(data["pool_id"], int) and data["pool_id"] >= 0, "pool_id должен быть неотрицательным целым"
        assert isinstance(data["atom_id"], int) and data["atom_id"] >= 0, "atom_id должен быть неотрицательным целым"
        assert isinstance(data["min_count"], int) and data["min_count"] >= 0
        assert isinstance(data["max_count"], int) and data["max_count"] >= 0
        assert data["min_count"] <= data["max_count"], "min_count не может быть больше max_count"

        assert isinstance(data["cost_price_active"], (int, float)) and data["cost_price_active"] >= 0
        assert isinstance(data["cost_price_passive"], (int, float)) and data["cost_price_passive"] >= 0

        assert isinstance(data["type_use"], int) and data["type_use"] in [0, 1, 2]  # уточни допустимые значения

        assert isinstance(data["created_at"], str), "created_at должно быть строкой"
        # Опционально: проверить формат ISO8601
        assert "T" in data["created_at"] and "Z" in data["created_at"], "created_at должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Успешно получена связь: ID={data['id']}, "
            f"Pool ID={data['pool_id']}, Atom ID={data['atom_id']}, Type Use={data['type_use']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
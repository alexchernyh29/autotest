# Создает новую связь между пулом ресурсов и атомом /api/v1/resource_pool_link_atom
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
    Получение токена аутентификации (копия из примера)
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


@allure.story("Создание связи между пулом ресурсов и атомом")
def test_create_resource_pool_atom_link():
    """
    Тест: создание связи между пулом ресурсов и атомом
    Эндпоинт: POST /api/v1/resource_pool_link_atom
    Поля: pool_id, atom_id, min_count, max_count, cost_price_active, cost_price_passive, type_use
    Проверяет:
      - успешный статус (200, 201)
      - корректный JSON в ответе
      - наличие ID и совпадение входных параметров
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Параметры связи (все из curl)
        pool_id = os.getenv("POOL_ID")
        atom_id = os.getenv("ATOM_ID")
        min_count = os.getenv("MIN_COUNT", "0")
        max_count = os.getenv("MAX_COUNT", "0")
        cost_price_active = os.getenv("COST_PRICE_ACTIVE", "0")
        cost_price_passive = os.getenv("COST_PRICE_PASSIVE", "0")
        type_use = os.getenv("TYPE_USE", "0")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert pool_id, "POOL_ID не задан в .env"
        assert atom_id, "ATOM_ID не задан в .env"

    # Приведение к нужным типам
    try:
        pool_id = int(pool_id)
        atom_id = int(atom_id)
        min_count = int(min_count)
        max_count = int(max_count)
        cost_price_active = float(cost_price_active)  # может быть дробным
        cost_price_passive = float(cost_price_passive)
        type_use = int(type_use)
    except (ValueError, TypeError) as e:
        pytest.fail(f"Ошибка преобразования параметров: {e}")

    assert pool_id >= 0, "POOL_ID должен быть неотрицательным"
    assert atom_id >= 0, "ATOM_ID должен быть неотрицательным"
    assert min_count >= 0, "MIN_COUNT должен быть >= 0"
    assert max_count >= 0, "MAX_COUNT должен быть >= 0"
    assert min_count <= max_count, "MIN_COUNT не может быть больше MAX_COUNT"
    assert type_use in [0, 1, 2], "TYPE_USE должен быть 0, 1 или 2 (или по документации)"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса"):
        payload = {
            "pool_id": pool_id,
            "atom_id": atom_id,
            "min_count": min_count,
            "max_count": max_count,
            "cost_price_active": cost_price_active,
            "cost_price_passive": cost_price_passive,
            "type_use": type_use
        }
        allure.attach(str(payload), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_pool_link_atom"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание связи"):
        response = requests.post(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code in [200, 201], (
            f"Ошибка создания связи. Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг и валидация JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        # Ожидаем, что ответ — объект со структурой
        required_fields = ["id", "pool_id", "atom_id", "min_count", "max_count",
                           "cost_price_active", "cost_price_passive", "type_use", "created_at"]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка типов
        assert isinstance(data["id"], int) and data["id"] > 0, "ID должен быть положительным целым"
        assert data["pool_id"] == pool_id, f"pool_id в ответе {data['pool_id']} ≠ ожидаемому {pool_id}"
        assert data["atom_id"] == atom_id, f"atom_id в ответе {data['atom_id']} ≠ ожидаемому {atom_id}"
        assert data["min_count"] == min_count, "min_count не совпадает"
        assert data["max_count"] == max_count, "max_count не совпадает"
        assert abs(data["cost_price_active"] - cost_price_active) < 1e-6, "cost_price_active не совпадает"
        assert abs(data["cost_price_passive"] - cost_price_passive) < 1e-6, "cost_price_passive не совпадает"
        assert data["type_use"] == type_use, "type_use не совпадает"
        assert isinstance(data["created_at"], str), "created_at должно быть строкой"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Связь успешно создана: ID={data['id']}, "
            f"Pool ID={pool_id}, Atom ID={atom_id}, Type Use={type_use}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
# Обновляет существующую связь между пулом ресурсов и атомом /api/v1/resource_pool_link_atom/{id}
import os
import pytest
import requests
import allure
from dotenv import load_dotenv
from pathlib import Path
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


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


@allure.story("Обновление связи между пулом ресурсов и атомом")
def test_update_resource_pool_atom_link():
    """
    Тест: обновление существующей связи по ID
    Эндпоинт: PUT /api/v1/resource_pool_link_atom/{id}
    Поля: pool_id, atom_id, min_count, max_count, cost_price_active, cost_price_passive, type_use
    Проверяет:
      - статус 200
      - валидный JSON в ответе
      - совпадение обновлённых полей
      - неизменность ID
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # ID связи для обновления
        link_id = os.getenv("RESOURCE_POOL_LINK_ID_TO_UPDATE")

        # Новые значения
        pool_id = os.getenv("UPDATE_POOL_ID")
        atom_id = os.getenv("UPDATE_ATOM_ID")
        min_count = os.getenv("UPDATE_MIN_COUNT", "1")
        max_count = os.getenv("UPDATE_MAX_COUNT", "10")
        cost_price_active = os.getenv("UPDATE_COST_PRICE_ACTIVE", "15.0")
        cost_price_passive = os.getenv("UPDATE_COST_PRICE_PASSIVE", "7.5")
        type_use = os.getenv("UPDATE_TYPE_USE", "1")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert link_id, "RESOURCE_POOL_LINK_ID_TO_UPDATE не задан в .env"
        assert pool_id, "UPDATE_POOL_ID не задан в .env"
        assert atom_id, "UPDATE_ATOM_ID не задан в .env"

    # Приведение типов
    try:
        link_id = int(link_id)
        pool_id = int(pool_id)
        atom_id = int(atom_id)
        min_count = int(min_count)
        max_count = int(max_count)
        cost_price_active = float(cost_price_active)
        cost_price_passive = float(cost_price_passive)
        type_use = int(type_use)
    except (ValueError, TypeError) as e:
        pytest.fail(f"Ошибка преобразования параметров: {e}")

    assert link_id > 0, "RESOURCE_POOL_LINK_ID_TO_UPDATE должен быть положительным"
    assert pool_id >= 0, "UPDATE_POOL_ID должен быть >= 0"
    assert atom_id >= 0, "UPDATE_ATOM_ID должен быть >= 0"
    assert min_count >= 0, "MIN_COUNT должен быть >= 0"
    assert max_count >= 0, "MAX_COUNT должен быть >= 0"
    assert min_count <= max_count, "MIN_COUNT не может быть больше MAX_COUNT"
    assert type_use in [0, 1, 2], "TYPE_USE должен быть 0, 1 или 2 (уточни по документации)"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса (новые значения)"):
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
        url = f"{base_url}/api/v1/resource_pool_link_atom/{link_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка PUT-запроса для обновления связи с ID={link_id}"):
        response = requests.put(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Связь с ID={link_id} не найдена. Проверьте ID.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректные данные или ID. Ответ: {response.text}")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    with allure.step("Парсинг и валидация ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        required_fields = [
            "id", "pool_id", "atom_id", "min_count", "max_count",
            "cost_price_active", "cost_price_passive", "type_use", "created_at"
        ]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка ID
        assert isinstance(data["id"], int) and data["id"] == link_id, f"ID в ответе ≠ {link_id}"

        # Проверка обновлённых значений
        assert data["pool_id"] == pool_id, f"pool_id: ожидаем {pool_id}, получено {data['pool_id']}"
        assert data["atom_id"] == atom_id, f"atom_id: ожидаем {atom_id}, получено {data['atom_id']}"
        assert data["min_count"] == min_count, f"min_count: ожидаем {min_count}, получено {data['min_count']}"
        assert data["max_count"] == max_count, f"max_count: ожидаем {max_count}, получено {data['max_count']}"
        assert abs(data["cost_price_active"] - cost_price_active) < 1e-6, "cost_price_active не совпадает"
        assert abs(data["cost_price_passive"] - cost_price_passive) < 1e-6, "cost_price_passive не совпадает"
        assert data["type_use"] == type_use, f"type_use: ожидаем {type_use}, получено {data['type_use']}"

        # created_at — не должен меняться, но проверим формат
        assert isinstance(data["created_at"], str), "created_at должно быть строкой"
        assert "T" in data["created_at"] and "Z" in data["created_at"], "created_at должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Связь успешно обновлена: ID={data['id']}, "
            f"Pool ID={data['pool_id']}, Atom ID={data['atom_id']}, "
            f"Min={data['min_count']}, Max={data['max_count']}, Type Use={data['type_use']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
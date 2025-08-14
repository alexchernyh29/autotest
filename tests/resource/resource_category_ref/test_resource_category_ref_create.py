# Создает новую категорию ресурса /api/v1/resource_category_ref
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


@allure.story("Создание новой категории ресурса")
def test_create_resource_category():
    """
    Тест: создание новой категории ресурса
    Эндпоинт: POST /api/v1/resource_category_ref
    Поля: type_ref_id, unit_measure_id, name, category_type_id
    Проверяет:
      - статус 200 или 201
      - валидный JSON в ответе
      - наличие ID и корректность полей
      - совпадение отправленных и полученных значений
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Параметры для создания категории
        name = os.getenv("CATEGORY_NAME")
        type_ref_id = os.getenv("CATEGORY_TYPE_REF_ID")
        unit_measure_id = os.getenv("CATEGORY_UNIT_MEASURE_ID")
        category_type_id = os.getenv("CATEGORY_TYPE_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert name and name.strip(), "CATEGORY_NAME не задан или пуст в .env"
        assert type_ref_id is not None, "CATEGORY_TYPE_REF_ID не задан"
        assert unit_measure_id is not None, "CATEGORY_UNIT_MEASURE_ID не задан"
        assert category_type_id is not None, "CATEGORY_TYPE_ID не задан"

    # Очистка и приведение типов
    name = name.strip()

    try:
        type_ref_id = int(type_ref_id)
        unit_measure_id = int(unit_measure_id)
        category_type_id = int(category_type_id)
    except (ValueError, TypeError) as e:
        pytest.fail(f"Ошибка преобразования числовых параметров: {e}")

    assert type_ref_id > 0, "CATEGORY_TYPE_REF_ID должен быть положительным"
    assert unit_measure_id > 0, "CATEGORY_UNIT_MEASURE_ID должен быть положительным"
    assert category_type_id > 0, "CATEGORY_TYPE_ID должен быть положительным"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса"):
        payload = {
            "type_ref_id": type_ref_id,
            "unit_measure_id": unit_measure_id,
            "name": name,
            "category_type_id": category_type_id
        }
        allure.attach(str(payload), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_category_ref"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка POST-запроса на создание категории"):
        response = requests.post(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code in [200, 201], (
            f"Ошибка при создании категории. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг и валидация JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        # Ожидаемые поля в ответе
        required_fields = ["id", "name", "type_ref_id", "unit_measure_id", "category_type_id", "created_at"]

        assert isinstance(data, dict), "Ожидался объект в ответе"
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка значений
        assert isinstance(data["id"], int) and data["id"] > 0, "ID должно быть положительным целым"
        assert data["name"] == name, f"Имя: ожидаем '{name}', получено '{data['name']}'"
        assert data["type_ref_id"] == type_ref_id, f"type_ref_id: ожидаем {type_ref_id}, получено {data['type_ref_id']}"
        assert data["unit_measure_id"] == unit_measure_id, f"unit_measure_id: ожидаем {unit_measure_id}, получено {data['unit_measure_id']}"
        assert data["category_type_id"] == category_type_id, f"category_type_id: ожидаем {category_type_id}, получено {data['category_type_id']}"

        assert isinstance(data["created_at"], str), "created_at должно быть строкой"
        assert "T" in data["created_at"] and "Z" in data["created_at"], "created_at должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Категория успешно создана: ID={data['id']}, Name='{data['name']}', "
            f"Type Ref ID={data['type_ref_id']}, Unit Measure ID={data['unit_measure_id']}, "
            f"Category Type ID={data['category_type_id']}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
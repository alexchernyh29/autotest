# test_get_resource_category_by_id.py

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
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

        response.raise_for_status()
        token_data = response.json()
        return token_data.get("tockenID")


@allure.story("Получение информации о категории ресурса по ID")
def test_get_resource_category_by_id():
    """
    Тест: получение категории ресурса по ID
    - Использует RESOURCE_CATEGORY_REF_ID из .env
    - Проверяет актуальную структуру ответа с вложенными объектами
    - Проверяет id, name и вложенные поля
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        category_id_str = os.getenv("RESOURCE_CATEGORY_REF_ID")  # Единый источник ID

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert category_id_str, "RESOURCE_CATEGORY_REF_ID не задан в .env"

    try:
        category_id = int(category_id_str)
        assert category_id > 0, "ID категории должно быть положительным целым числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_CATEGORY_REF_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для GET /resource_category_ref/{category_id}"):
        url = f"{base_url}/api/v1/resource_category_ref/{category_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

    with allure.step("Отправка GET-запроса"):
        response = requests.get(url, headers=headers)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text or "null", "Response Body", AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Категория с ID={category_id} не найдена. Проверьте, существует ли она.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный формат ID: {category_id}")
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), "Parsed Response", AttachmentType.JSON)

    with allure.step("Проверка структуры и значений ответа"):
        # Основные поля верхнего уровня
        required_fields = ["id", "name", "unitMeasure", "typeRef", "category_type"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка ID
        assert isinstance(data["id"], int), "'id' должно быть числом"
        assert data["id"] == category_id, f"Ожидался ID={category_id}, получен {data['id']}"

        # Проверка name
        assert isinstance(data["name"], str), "'name' должно быть строкой"
        assert len(data["name"]) > 0, "'name' не должно быть пустым"

        # Проверка вложенных объектов
        for field_name, id_field in [
            ("unitMeasure", "unit_measure_id"),
            ("typeRef", "type_ref_id"),
            ("category_type", "category_type_id")
        ]:
            assert isinstance(data[field_name], dict), f"'{field_name}' должно быть объектом"
            nested = data[field_name]
            assert "id" in nested, f"'{field_name}.id' отсутствует"
            assert isinstance(nested["id"], int), f"'{field_name}.id' должно быть числом"
            assert nested["id"] > 0, f"'{field_name}.id' должно быть положительным"
            assert "name" in nested, f"'{field_name}.name' отсутствует"
            assert isinstance(nested["name"], str), f"'{field_name}.name' должно быть строкой"

    with allure.step("Тест успешно пройден"):
        allure.attach(
            f"Категория получена: ID={data['id']}, Name='{data['name']}', "
            f"TypeRef ID={data['typeRef']['id']}, UnitMeasure ID={data['unitMeasure']['id']}, "
            f"Category Type ID={data['category_type']['id']}",
            "Результат",
            AttachmentType.TEXT
        )
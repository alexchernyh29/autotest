# test_get_resource_location_by_id.py

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


@allure.story("Получение информации о местоположении ресурса по ID")
def test_get_resource_location_by_id():
    """
    Тест: получение данных о местоположении по ID
    - Использует RESOURCE_LOCATION_ID из .env
    - Проверяет статус 200
    - Валидирует структуру и поля по актуальному ответу API
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        location_id_str = os.getenv("RESOURCE_LOCATION_ID")  # Берём ID из .env

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert location_id_str, "RESOURCE_LOCATION_ID не задан в .env"

    try:
        location_id = int(location_id_str)
        assert location_id > 0, "RESOURCE_LOCATION_ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_LOCATION_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step(f"Формирование URL для GET /resource_location/{location_id}"):
        url = f"{base_url}/api/v1/resource_location/{location_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

    with allure.step("Отправка GET-запроса"):
        response = requests.get(url, headers=headers)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Местоположение с ID={location_id} не найдено. Проверьте, существует ли оно.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректный формат ID: {location_id}")
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), "Parsed Response", AttachmentType.JSON)

    with allure.step("Проверка структуры и значений ответа"):
        # Обязательные поля верхнего уровня
        required_fields = ["id", "name", "address", "create_time", "update_time", "create_user_id", "update_user_id"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка ID
        assert isinstance(data["id"], int), "'id' должно быть числом"
        assert data["id"] == location_id, f"Ожидался ID={location_id}, получен ID={data['id']}"

        # Проверка строк
        assert isinstance(data["name"], str), "'name' должно быть строкой"
        assert data["name"] == "Облако автотеста", f"Ожидалось name='Облако автотеста', получено: {data['name']}"

        assert isinstance(data["address"], str), "'address' должно быть строкой"
        assert data["address"] == "РФ, Москва", f"Ожидался address='РФ, Москва', получен: {data['address']}"

        # Проверка create_user_id и update_user_id
        assert isinstance(data["create_user_id"], int), "'create_user_id' должно быть числом"
        assert isinstance(data["update_user_id"], int), "'update_user_id' должно быть числом"

        # Проверка вложенных объектов времени
        for time_field in ["create_time", "update_time"]:
            assert isinstance(data[time_field], dict), f"'{time_field}' должно быть объектом"
            time_obj = data[time_field]
            assert "date" in time_obj, f"'{time_field}.date' отсутствует"
            assert isinstance(time_obj["date"], str), f"'{time_field}.date' должно быть строкой"
            assert "timezone_type" in time_obj, f"'{time_field}.timezone_type' отсутствует"
            assert isinstance(time_obj["timezone_type"], int), f"'{time_field}.timezone_type' должно быть числом"
            assert "timezone" in time_obj, f"'{time_field}.timezone' отсутствует"
            assert isinstance(time_obj["timezone"], str), f"'{time_field}.timezone' должно быть строкой"

        # Проверка формата даты (упрощённо)
        create_date = data["create_time"]["date"]
        assert "2025-" in create_date or "2024-" in create_date or "2023-" in create_date, \
            f"Некорректный формат даты create_time.date: {create_date}"

        update_date = data["update_time"]["date"]
        assert "2025-" in update_date or "2024-" in update_date or "2023-" in update_date, \
            f"Некорректный формат даты update_time.date: {update_date}"

    with allure.step("Тест успешно пройден"):
        allure.attach(
            f"Получено местоположение: ID={data['id']}, Name='{data['name']}', "
            f"Address='{data['address']}', Created by={data['create_user_id']}",
            "Результат",
            attachment_type=AttachmentType.TEXT
        )
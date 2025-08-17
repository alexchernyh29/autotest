# test_update_resource_location.py

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


@allure.story("Обновление информации о местоположении ресурса")
def test_update_resource_location():
    """
    Тест: обновление местоположения ресурса
    - Использует фиксированные данные
    - Берёт ID из RESOURCE_LOCATION_ID
    - Проверяет статус 200
    - Если есть тело ответа — проверяет структуру
    - Если тело null — пропускает проверку полей
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        location_id_str = os.getenv("RESOURCE_LOCATION_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert location_id_str, "RESOURCE_LOCATION_ID не задан в .env"

    try:
        location_id = int(location_id_str)
        assert location_id > 0, "RESOURCE_LOCATION_ID должен быть положительным целым числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_LOCATION_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    # Фиксированные данные для обновления
    updated_name = "Оновлённое имя Облака Автотеста"
    updated_address = "РФ, Москва, Китай-город"

    with allure.step("Формирование тела запроса (обновлённые данные)"):
        payload = {
            "name": updated_name,
            "address": updated_address
        }
        allure.attach(str(payload), "Request Body", AttachmentType.JSON)

    with allure.step(f"Формирование URL для PUT /resource_location/{location_id}"):
        url = f"{base_url}/api/v1/resource_location/{location_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

    with allure.step("Отправка PUT-запроса"):
        response = requests.put(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text or "null", "Response Body", AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data) if data is not None else "null", "Parsed Response", AttachmentType.TEXT)

    # Проверка структуры — только если ответ не null
    if data is None:
        with allure.step("Ответ — null. Пропуск проверки полей (допустимо для PUT)"):
            allure.attach(
                "Сервер вернул null, но статус 200 — это допустимо при обновлении",
                "Внимание",
                AttachmentType.TEXT
            )
    else:
        with allure.step("Проверка структуры и значений ответа"):
            required_fields = ["id", "name", "address", "create_time", "update_time", "create_user_id", "update_user_id"]
            missing = [field for field in required_fields if field not in data]
            assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

            assert isinstance(data["id"], int), "'id' должно быть числом"
            assert data["id"] == location_id, f"ID изменился: ожидался {location_id}, получен {data['id']}"

            assert data["name"] == updated_name, f"Ожидалось name='{updated_name}', получено: {data['name']}"
            assert data["address"] == updated_address, f"Ожидалось address='{updated_address}', получено: {data['address']}"

            assert isinstance(data["create_user_id"], int), "'create_user_id' должно быть числом"
            assert isinstance(data["update_user_id"], int), "'update_user_id' должно быть числом"

            for field_name in ["create_time", "update_time"]:
                assert isinstance(data[field_name], dict), f"'{field_name}' должно быть объектом"
                time_obj = data[field_name]
                assert "date" in time_obj, f"'{field_name}.date' отсутствует"
                assert isinstance(time_obj["date"], str), f"'{field_name}.date' должно быть строкой"
                assert "timezone_type" in time_obj, f"'{field_name}.timezone_type' отсутствует"
                assert isinstance(time_obj["timezone_type"], int), f"'{field_name}.timezone_type' должно быть числом"
                assert "timezone" in time_obj, f"'{field_name}.timezone' отсутствует"
                assert isinstance(time_obj["timezone"], str), f"'{field_name}.timezone' должно быть строкой"

    with allure.step("Тест успешно пройден"):
        allure.attach(
            f"Местоположение с ID={location_id} обновлено. Статус: 200",
            "Результат",
            AttachmentType.TEXT
        )
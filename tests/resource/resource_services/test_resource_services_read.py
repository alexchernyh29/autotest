# tests/resource_service/test_get_resource_services.py

import os
import pytest
import json
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
    return token_data.get("tockenID")  # Обратите внимание на опечатку: tockenID


@allure.story("Получение списка всех сервисов ресурсов (resource_services)")
def test_get_resource_services():
    """
    Тест получения списка всех сервисов ресурсов
    Проверяет:
    1. Успешный статус-код (200)
    2. Ответ в формате JSON
    3. Наличие массива данных
    4. Структуру каждого элемента (id, name, system_name, create_time и др.)
    5. Непустой ответ (если ожидается)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_services"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка GET-запроса к /resource_services"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении списка сервисов ресурсов. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name="Parsed Response Data",
            attachment_type=AttachmentType.JSON
        )

        assert isinstance(data, list), "Ожидался массив сервисов ресурсов"

    if len(data) == 0:
        with allure.step("Внимание: список сервисов пуст"):
            allure.attach(
                "Справочник resource_services вернул пустой массив. Проверьте, заполнены ли данные в системе.",
                name="Предупреждение",
                attachment_type=AttachmentType.TEXT
            )
        return

    with allure.step(f"Проверка структуры каждого из {len(data)} элементов"):
        required_fields = ["id", "name", "system_name", "create_time", "update_time", "create_user_id", "update_user_id"]

        for idx, service in enumerate(data):
            with allure.step(f"Сервис #{idx + 1} (ID={service.get('id')})"):
                assert isinstance(service, dict), "Каждый элемент должен быть объектом"

                # Проверка обязательных полей
                missing = [field for field in required_fields if field not in service]
                assert not missing, f"Отсутствуют поля: {', '.join(missing)}"

                # Проверка типов
                assert isinstance(service["id"], int), "Поле 'id' должно быть целым числом"
                assert isinstance(service["name"], str), "Поле 'name' должно быть строкой"
                assert isinstance(service["system_name"], str), "Поле 'system_name' должно быть строкой"
                assert isinstance(service["create_user_id"], int), "Поле 'create_user_id' должно быть числом"
                assert isinstance(service["update_user_id"], int), "Поле 'update_user_id' должно быть числом"

                # Проверка времени
                for time_field in ["create_time", "update_time"]:
                    time_obj = service[time_field]
                    assert isinstance(time_obj, dict), f"Поле '{time_field}' должно быть объектом"
                    assert "date" in time_obj, f"В '{time_field}' отсутствует 'date'"
                    assert "timezone_type" in time_obj, f"В '{time_field}' отсутствует 'timezone_type'"
                    assert "timezone" in time_obj, f"В '{time_field}' отсутствует 'timezone'"
                    assert isinstance(time_obj["date"], str), f"date в '{time_field}' должно быть строкой"
                    assert isinstance(time_obj["timezone_type"], int), f"timezone_type в '{time_field}' должно быть числом"
                    assert isinstance(time_obj["timezone"], str), f"timezone в '{time_field}' должно быть строкой"

                # Проверка, что строки не пустые
                assert service["name"].strip() != "", "Поле 'name' не должно быть пустым"
                assert service["system_name"].strip() != "", "Поле 'system_name' не должно быть пустым"

    with allure.step("✅ Тест завершён успешно"):
        allure.attach(
            f"Успешно получено {len(data)} сервисов ресурсов.",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
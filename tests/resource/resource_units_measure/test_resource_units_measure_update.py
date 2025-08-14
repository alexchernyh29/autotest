# Обновляет информацию о существующей единице измерения ресурсов /api/v1/resource_unit_measure/{id}
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


@allure.story("Обновление единицы измерения по ID (PUT)")
def test_update_resource_unit_measure():
    """
    Тест обновления единицы измерения через PUT /api/v1/resource_unit_measure/{id}
    Проверяет:
    1. Успешный статус-код (200)
    2. Валидность ответа
    3. Соответствие обновлённых данных
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        unit_id = os.getenv("RESOURCE_UNIT_MEASURE_ID", "1232131")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert unit_id, "RESOURCE_UNIT_MEASURE_ID не задан"

    try:
        unit_id = int(unit_id)
        assert unit_id > 0, "ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("RESOURCE_UNIT_MEASURE_ID должен быть целым числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен"

    # Подготовка данных для обновления
    updated_name = f"Обновлённое имя {unit_id}"

    with allure.step(f"Формирование тела запроса для обновления (ID={unit_id})"):
        request_body = {
            "name": updated_name
        }
        allure.attach(str(request_body), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_unit_measure/{unit_id}"
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка PUT-запроса"):
        response = requests.put(url, json=request_body, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ошибка при обновлении единицы измерения. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка структуры ответа"):
        required_fields = ["id", "name"]
        missing = [field for field in required_fields if field not in data]
        assert not missing, f"Отсутствуют поля: {', '.join(missing)}"

        assert data["id"] == unit_id, f"ID в ответе ({data['id']}) не совпадает с запрошенным ({unit_id})"
        assert data["name"] == updated_name, f"Имя не обновилось: ожидается '{updated_name}', получено '{data['name']}'"

    with allure.step("Тест успешно пройден"):
        allure.attach(
            f"Обновлено: ID={data['id']}, Name='{data['name']}'",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
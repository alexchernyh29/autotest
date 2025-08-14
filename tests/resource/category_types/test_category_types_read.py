# Получить список всех типов категорий /api/v1/resource/category_types
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

    response.raise_for_status()  # Проверка на ошибки HTTP

    token_data = response.json()
    return token_data.get("tockenID")  # Предполагается, что ответ содержит поле "tockenID"


@allure.story("Получение типов категорий ресурсов")
def test_get_category_types():
    """
    Тест получения списка типов категорий ресурсов
    Проверяет:
    1. Успешный статус-код (200)
    2. Ответ в формате JSON
    3. Наличие ожидаемых полей в каждом элементе
    4. Непустой ответ (если ожидается хотя бы один элемент)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Получение параметров из .env"):
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
        assert token, "Не удалось получить токен"

    with allure.step("Формирование запроса к /resource/category_types"):
        url = f"{base_url}/api/v1/resource/category_types"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(f"URL: {url}", name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.TEXT)

    with allure.step("Отправка GET-запроса к /resource/category_types"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка статус-кода ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении типов категорий. "
            f"Status: {response.status_code}, Response: {response.text}"
        )

    with allure.step("Парсинг и проверка структуры ответа"):
        try:
            data = response.json()
        except Exception as e:
            allure.attach(response.text, name="Invalid JSON Response", attachment_type=AttachmentType.TEXT)
            pytest.fail(f"Ответ не в формате JSON: {e}")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        assert isinstance(data, list), "Ожидается, что ответ — массив объектов"

    if len(data) == 0:
        with allure.step("Предупреждение: список типов категорий пуст"):
            allure.attach("Список category_types пуст, возможно, это ожидаемо.", name="Warning", attachment_type=AttachmentType.TEXT)
    else:
        with allure.step("Проверка структуры элементов в списке"):
            required_fields = ["id", "name", "code"]
            for idx, item in enumerate(data):
                assert isinstance(item, dict), f"Элемент под индексом {idx} не является объектом"
                missing_fields = [field for field in required_fields if field not in item]
                assert not missing_fields, f"В элементе {idx} отсутствуют поля: {missing_fields}"

    with allure.step("Тест завершён успешно"):
        allure.attach(f"Получено {len(data)} типов категорий", name="Результат", attachment_type=AttachmentType.TEXT)
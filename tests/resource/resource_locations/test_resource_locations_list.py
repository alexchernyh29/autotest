# Возвращает список всех местоположений ресурсов /api/v1/resource_locations
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


@allure.story("Получение списка всех местоположений ресурсов")
def test_get_resource_locations():
    """
    Тест: получение списка всех местоположений ресурсов
    Эндпоинт: GET /api/v1/resource_locations
    Проверяет:
      - статус 200
      - ответ в формате JSON
      - наличие массива данных
      - структуру каждого элемента
      - обязательные поля
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
        url = f"{base_url}/api/v1/resource_locations"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка GET-запроса для получения списка местоположений"):
        response = requests.get(url, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении списка местоположений. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        assert isinstance(data, list), "Ожидался массив местоположений"

    if len(data) == 0:
        with allure.step("Внимание: список местоположений пуст"):
            allure.attach(
                "API вернул пустой список. Проверьте, есть ли активные местоположения в системе.",
                name="Предупреждение",
                attachment_type=AttachmentType.TEXT
            )
    else:
        with allure.step(f"Проверка структуры {len(data)} элементов"):
            # Пример обязательных полей (можно уточнить по реальному API)
            required_fields = ["id", "name", "code", "status_id", "created_at"]

            for idx, location in enumerate(data):
                assert isinstance(location, dict), f"Элемент [{idx}] не является объектом"

                missing = [field for field in required_fields if field not in location]
                assert not missing, f"В элементе [{idx}] отсутствуют поля: {', '.join(missing)}"

                # Проверка типов
                assert isinstance(location["id"], int) and location["id"] > 0, f"ID элемента [{idx}] должно быть положительным числом"
                assert isinstance(location["name"], str) and len(location["name"]) > 0, f"name элемента [{idx}] должно быть непустой строкой"
                assert isinstance(location["code"], str), f"code элемента [{idx}] должно быть строкой"
                assert isinstance(location["status_id"], int), f"status_id элемента [{idx}] должно быть числом"
                assert isinstance(location["created_at"], str), f"created_at элемента [{idx}] должно быть строкой"
                assert "T" in location["created_at"] and "Z" in location["created_at"], f"created_at элемента [{idx}] должно быть в формате ISO8601"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Получено {len(data)} местоположений ресурсов.",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
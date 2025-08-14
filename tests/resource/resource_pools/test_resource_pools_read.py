# Возвращает список пулов ресурсов /api/v1/resource_pools?by_service_id={id}&by_location_id={id}
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


@allure.story("Получение списка пулов ресурсов с фильтрацией")
def test_get_resource_pools_filtered():
    """
    Тест получения списка пулов ресурсов с фильтрами:
    - by_service_id=1
    - by_location_id=1
    Проверяет:
    1. Успешный статус-код (200)
    2. Ответ в формате JSON
    3. Наличие массива данных
    4. Соответствие структуры элементов
    5. Опционально: проверка соответствия фильтрам
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Значения по умолчанию или из .env
        service_id = os.getenv("FILTER_BY_SERVICE_ID", "1")
        location_id = os.getenv("FILTER_BY_LOCATION_ID", "1")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert service_id, "FILTER_BY_SERVICE_ID не задан"
        assert location_id, "FILTER_BY_LOCATION_ID не задан"

    try:
        service_id = int(service_id)
        location_id = int(location_id)
        assert service_id > 0, "by_service_id должен быть положительным числом"
        assert location_id > 0, "by_location_id должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("FILTER_BY_SERVICE_ID и FILTER_BY_LOCATION_ID должны быть целыми числами")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование параметров запроса (query params)"):
        params = {
            "by_service_id": service_id,
            "by_location_id": location_id
        }
        allure.attach(str(params), name="Query Parameters", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_pools"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Отправка GET-запроса с фильтрами"):
        response = requests.get(url, headers=headers, params=params)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении пулов ресурсов. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        assert isinstance(data, list), "Ожидался массив пулов ресурсов"

    if len(data) == 0:
        with allure.step("Внимание: список пулов ресурсов пуст"):
            allure.attach(
                "Фильтр вернул пустой список. Проверьте, существуют ли пулы с by_service_id=1 и by_location_id=1.",
                name="Предупреждение",
                attachment_type=AttachmentType.TEXT
            )
    else:
        with allure.step("Проверка структуры элементов в списке"):
            # Базовые обязательные поля (можно уточнить по реальному ответу)
            required_fields = ["id", "name", "service_id", "location_id", "pool_type"]

            for idx, pool in enumerate(data):
                assert isinstance(pool, dict), f"Элемент [{idx}] не является объектом"

                missing = [field for field in required_fields if field not in pool]
                assert not missing, f"В элементе [{idx}] отсутствуют обязательные поля: {', '.join(missing)}"

                # Проверка типов
                assert isinstance(pool["id"], int), f"id элемента [{idx}] должно быть числом"
                assert isinstance(pool["name"], str), f"name элемента [{idx}] должно быть строкой"
                assert isinstance(pool["service_id"], int), f"service_id элемента [{idx}] должно быть числом"
                assert isinstance(pool["location_id"], int), f"location_id элемента [{idx}] должно быть числом"
                assert isinstance(pool["pool_type"], (str, type(None))), f"pool_type элемента [{idx}] должно быть строкой или null"

                # Проверка соответствия фильтрам (опционально)
                assert pool["service_id"] == service_id, (
                    f"Пул ID={pool['id']} имеет service_id={pool['service_id']}, ожидался {service_id}"
                )
                assert pool["location_id"] == location_id, (
                    f"Пул ID={pool['id']} имеет location_id={pool['location_id']}, ожидался {location_id}"
                )

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Получено {len(data)} пулов ресурсов с by_service_id={service_id} и by_location_id={location_id}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
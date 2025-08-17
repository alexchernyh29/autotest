import os
import requests
import allure
import pytest
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
        response.raise_for_status()

        token_data = response.json()
        return token_data.get("tockenID")


@allure.story("Получение списка пулов ресурсов с фильтрацией")
def test_get_resource_pools_filtered():
    """
    Тест проверяет:
    1. Получение пулов ресурсов с фильтрами by_service_id и by_location_id
    2. Все элементы имеют service_id == переданному
    3. Все элементы имеют location.id == переданному
    4. Подсчёт количества элементов (по id)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Значения фильтров — из .env или по умолчанию
        service_id = os.getenv("FILTER_BY_SERVICE_ID", "414")
        location_id = os.getenv("FILTER_BY_LOCATION_ID", "125")

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

    with allure.step("Формирование параметров запроса"):
        params = {
            "by_service_id": service_id,
            "by_location_id": location_id
        }
        allure.attach(str(params), "Query Parameters", AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_pools"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, "Request URL", AttachmentType.TEXT)
        allure.attach(str(headers), "Request Headers", AttachmentType.JSON)

    with allure.step("Отправка GET-запроса"):
        response = requests.get(url, headers=headers, params=params)

        allure.attach(str(response.status_code), "Response Status Code", AttachmentType.TEXT)
        allure.attach(response.text, "Response Body", AttachmentType.TEXT)
        allure.attach(str(dict(response.headers)), "Response Headers", AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении пулов ресурсов. Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), "Parsed Response", AttachmentType.JSON)

        assert isinstance(data, list), "Ожидался массив пулов ресурсов"

    with allure.step("Проверка соответствия фильтрам и подсчёт id"):
        if len(data) == 0:
            pytest.fail("Ответ вернул пустой список. Проверьте, существуют ли данные для указанных фильтров.")

        received_ids = []

        for idx, pool in enumerate(data):
            assert isinstance(pool, dict), f"Элемент [{idx}] не является объектом"

            # Проверка обязательных полей
            assert "id" in pool, f"Отсутствует 'id' в элементе [{idx}]"
            assert "service_id" in pool, f"Отсутствует 'service_id' в элементе [{idx}]"
            assert "location" in pool, f"Отсутствует 'location' в элементе [{idx}]"
            assert isinstance(pool["location"], dict), f"'location' должен быть объектом в элементе [{idx}]"
            assert "id" in pool["location"], f"Отсутствует 'location.id' в элементе [{idx}]"

            # Собираем id
            received_ids.append(pool["id"])

            # Проверка фильтров
            assert pool["service_id"] == service_id, (
                f"Пул ID={pool['id']} имеет service_id={pool['service_id']}, ожидался {service_id}"
            )
            assert pool["location"]["id"] == location_id, (
                f"Пул ID={pool['id']} имеет location.id={pool['location']['id']}, ожидался {location_id}"
            )

        # Подсчёт и вывод количества
        count = len(received_ids)
        unique_count = len(set(received_ids))

        with allure.step("Проверка уникальности id"):
            assert count == unique_count, "Обнаружены дубликаты id в ответе"

        with allure.step("Результат подсчёта"):
            allure.attach(
                f"Найдено {count} уникальных пулов ресурсов с by_service_id={service_id} и by_location_id={location_id}",
                "Количество элементов",
                AttachmentType.TEXT
            )
            allure.attach(
                ", ".join(map(str, sorted(received_ids))),
                "Список ID",
                AttachmentType.TEXT
            )

    # Финальная проверка — можно использовать значение в других тестах
    assert count > 0, "Не найдено ни одного пула ресурсов по заданным фильтрам"
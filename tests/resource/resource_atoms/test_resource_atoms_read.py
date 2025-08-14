# Получить список атомов ресурсов /api/v1/resource_atoms?by_pool_id={id}&by_category_id={id}
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


@allure.story("Получение списка атомов ресурсов с фильтрацией")
def test_get_resource_atoms_filtered():
    """
    Тест: получение списка атомов ресурсов с фильтрами:
    - by_pool_id
    - by_category_id
    Проверяет:
      - статус 200
      - ответ в формате JSON
      - наличие массива данных
      - структуру элементов
      - соответствие фильтрам (опционально)
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Фильтры
        by_pool_id = os.getenv("FILTER_BY_POOL_ID", "2")
        by_category_id = os.getenv("FILTER_BY_CATEGORY_ID", "1")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert by_pool_id, "FILTER_BY_POOL_ID не задан в .env"
        assert by_category_id, "FILTER_BY_CATEGORY_ID не задан в .env"

    try:
        by_pool_id = int(by_pool_id)
        by_category_id = int(by_category_id)
        assert by_pool_id > 0, "FILTER_BY_POOL_ID должен быть положительным числом"
        assert by_category_id > 0, "FILTER_BY_CATEGORY_ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("FILTER_BY_POOL_ID и FILTER_BY_CATEGORY_ID должны быть целыми положительными числами")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование параметров запроса (query params)"):
        params = {
            "by_pool_id": by_pool_id,
            "by_category_id": by_category_id
        }
        allure.attach(str(params), name="Query Parameters", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_atoms"
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
            f"Ошибка при получении атомов ресурсов. "
            f"Статус: {response.status_code}, Ответ: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed Response Data", attachment_type=AttachmentType.JSON)

        assert isinstance(data, list), "Ожидался массив атомов ресурсов"

    if len(data) == 0:
        with allure.step("Внимание: список атомов пуст"):
            allure.attach(
                f"Фильтр by_pool_id={by_pool_id} и by_category_id={by_category_id} вернул пустой список. "
                "Проверьте, существуют ли атомы, соответствующие этим критериям.",
                name="Предупреждение",
                attachment_type=AttachmentType.TEXT
            )
    else:
        with allure.step(f"Проверка структуры {len(data)} атомов"):
            # Пример обязательных полей (можно уточнить по API)
            required_fields = ["id", "name", "pool_id", "category_id", "unit", "value", "status_id"]

            for idx, atom in enumerate(data):
                assert isinstance(atom, dict), f"Элемент [{idx}] не является объектом"

                missing = [field for field in required_fields if field not in atom]
                assert not missing, f"В элементе [{idx}] отсутствуют поля: {', '.join(missing)}"

                # Проверка типов
                assert isinstance(atom["id"], int) and atom["id"] > 0, f"id элемента [{idx}] должно быть положительным"
                assert isinstance(atom["name"], str) and len(atom["name"]) > 0, f"name элемента [{idx}] — непустая строка"
                assert atom["pool_id"] == by_pool_id, f"pool_id элемента [{idx}] ≠ фильтру {by_pool_id}"
                assert atom["category_id"] == by_category_id, f"category_id элемента [{idx}] ≠ фильтру {by_category_id}"
                assert isinstance(atom["unit"], str), f"unit элемента [{idx}] должно быть строкой"
                assert isinstance(atom["value"], (int, float)), f"value элемента [{idx}] должно быть числом"
                assert isinstance(atom["status_id"], int), f"status_id элемента [{idx}] должно быть числом"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Получено {len(data)} атомов ресурсов с by_pool_id={by_pool_id} и by_category_id={by_category_id}.",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
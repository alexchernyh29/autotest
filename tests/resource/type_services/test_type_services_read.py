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
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)

    response.raise_for_status()

    token_data = response.json()
    return token_data.get("tockenID")


# Ожидаемый ответ
EXPECTED_TYPE_SERVICES = [
    {
        "id": 1,
        "name": "Нематериальная услуга",
        "sysname": "simple"
    },
    {
        "id": 2,
        "name": "Услуга аренды отдельной облачной службы",
        "sysname": "service"
    },
    {
        "id": 3,
        "name": "Услуга аренды облачного сервиса",
        "sysname": "cloud"
    },
    {
        "id": 4,
        "name": "Услуга аренды программного обеспечения",
        "sysname": "software"
    },
    {
        "id": 6,
        "name": "Услуга аренды оборудования",
        "sysname": "hardware"
    },
    {
        "id": 7,
        "name": "Услуга размещения оборудования",
        "sysname": "colacation"
    },
    {
        "id": 8,
        "name": "Услуга аренды почтового сервиса",
        "sysname": "mail"
    }
]


@allure.story("Получение типов услуг")
def test_get_type_services():
    """
    Тест получения списка типов услуг (type_services)
    Проверяет:
    1. Статус 200
    2. Ответ — валидный JSON и массив
    3. Структуру каждого элемента: id, name, sysname
    4. Полное соответствие ожидаемому списку (включая порядок и значения)
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

    with allure.step("Формирование URL и заголовков для запроса /resource/type_services"):
        url = f"{base_url}/api/v1/resource/type_services"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.TEXT)

    with allure.step("Отправка GET-запроса к /resource/type_services"):
        response = requests.get(url, headers=headers)
        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.TEXT)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, (
            f"Запрос к /resource/type_services завершился с ошибкой. "
            f"Статус: {response.status_code}, Тело: {response.text}"
        )

    with allure.step("Парсинг JSON-ответа"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="Parsed JSON Response", attachment_type=AttachmentType.JSON)

        assert isinstance(data, list), "Ожидался массив типов услуг"

    with allure.step("Проверка структуры и содержимого каждого элемента"):
        required_fields = ["id", "name", "sysname"]
        for idx, service in enumerate(data):
            assert isinstance(service, dict), f"Элемент {idx} не является объектом"
            missing = [field for field in required_fields if field not in service]
            assert not missing, f"В типе услуги {idx} отсутствуют поля: {', '.join(missing)}"

    with allure.step("Проверка полного соответствия ожидаемому списку"):
        assert data == EXPECTED_TYPE_SERVICES, (
            "Ответ не соответствует ожидаемому списку типов услуг.\n"
            f"Ожидалось: {EXPECTED_TYPE_SERVICES}\n"
            f"Получено: {data}"
        )

    with allure.step("Тест успешно пройден"):
        allure.attach(f"Получено {len(data)} типов услуг. Ответ полностью соответствует ожидаемому.", 
                      name="Результат", attachment_type=AttachmentType.TEXT)
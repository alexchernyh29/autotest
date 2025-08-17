import os
import pytest
import requests
import allure
from dotenv import load_dotenv, find_dotenv, set_key
from pathlib import Path
from faker import Faker

# Инициализация Faker
fake = Faker()

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

# Глобальные переменные для хранения данных
CREATED_ORGANIZATION_DATA = {}
CREATED_ORGANIZATION_ID = None

@allure.step("Получение токена аутентификации")
def get_auth_token(base_url, login, password, timeoutlive, domain):
    """Получение токена аутентификации"""
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {"accept": "application/json"}
    
    allure.attach(
        f"curl -X POST '{url}?login={login}&password=*****&timeoutlive={timeoutlive}&domain={domain}' "
        f"-H 'accept: application/json'",
        name="CURL команда",
        attachment_type=allure.attachment_type.TEXT
    )
    
    response = requests.post(url, headers=headers, params=params)
    allure.attach(
        f"Status Code: {response.status_code}\nResponse: {response.text}",
        name="Response Details",
        attachment_type=allure.attachment_type.TEXT
    )
    
    response.raise_for_status()
    token = response.json().get("tockenID")
    
    if token:
        allure.attach(
            f"Полученный токен (первые 10 символов): {token[:10]}...",
            name="Токен",
            attachment_type=allure.attachment_type.TEXT
        )
    
    return token

@allure.feature("Организации")
def test_create_organization():
    """Тест создания организации со случайными данными"""
    global CREATED_ORGANIZATION_DATA, CREATED_ORGANIZATION_ID
    
    with allure.step("Подготовка тестовых данных"):
        # Загрузка переменных окружения
        load_dotenv(ENV_FILE)

        # Получение параметров из .env
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"

    with allure.step("Получение токена авторизации"):
        token_id = get_auth_token(base_url, login, password, 600, domain)
        assert token_id, "Не удалось получить tockenID"

    with allure.step("Генерация тестовых данных организации"):
        CREATED_ORGANIZATION_DATA = {
            "name": fake.company(),
            "number_contract": str(fake.random_number(digits=10)),
            "cid": str(fake.random_number(digits=4)),
            "contract_begin_time": "2025-07-16",
            "address": fake.address(),
            "fact_address": fake.address(),
            "contact_name": fake.name(),
            "contact_data": fake.job(),
            "contact_phone": fake.phone_number(),
            "contact_mail": fake.email(),
            "description": fake.text(),
            "inn": str(fake.random_number(digits=10)),
            "kpp": str(fake.random_number(digits=6)),
            "bik": str(fake.random_number(digits=9)),
            "pay_account": str(fake.random_number(digits=12)),
            "kor_account": str(fake.random_number(digits=10)),
            "bank_name": fake.company(),
            "sub_right_ref_id": 2,
            "manager_id": 434,
            "tenant_id": 123,
            "type_right_ref_id": 9
        }
        
        allure.attach(
            str(CREATED_ORGANIZATION_DATA),
            name="Данные для создания организации",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Отправка запроса на создание организации"):
        url = f"{base_url}/api/v1/organization"
        
        allure.attach(
            f"curl -X POST '{url}' "
            f"-H 'accept: application/json' "
            f"-H 'content-type: application/json' "
            f"-H 'tockenid: {token_id}' "
            f"-d '{str(CREATED_ORGANIZATION_DATA).replace("'", '"')}'",
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = requests.post(
            url,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "tockenid": token_id
            },
            json=CREATED_ORGANIZATION_DATA
        )
        
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Проверка ответа"):
        assert response.status_code == 200, (
            f"Ошибка при создании организации. "
            f"Status: {response.status_code}, Response: {response.text}"
        )

        response_data = response.json()
        assert "id" in response_data, "Отсутствует поле id в ответе"
        
        allure.attach(
            str(response_data),
            name="Ответ сервера",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Сохранение ID организации"):
        CREATED_ORGANIZATION_ID = str(response_data["id"])
        set_key(ENV_FILE, "ORGANIZATION_ID", CREATED_ORGANIZATION_ID)
        
        allure.attach(
            f"ID созданной организации: {CREATED_ORGANIZATION_ID}",
            name="ID организации",
            attachment_type=allure.attachment_type.TEXT
        )

@allure.feature("Организации")
def test_verify_created_organization():
    """Тест проверки созданной организации"""
    global CREATED_ORGANIZATION_DATA, CREATED_ORGANIZATION_ID
    
    with allure.step("Проверка наличия ID организации"):
        assert CREATED_ORGANIZATION_ID is not None, "ID организации не был сохранен в переменной"
        
        load_dotenv(ENV_FILE)
        assert os.getenv("ORGANIZATION_ID"), "ID организации не найден в .env файле"

    with allure.step("Подготовка тестовых данных"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")

    with allure.step("Получение токена авторизации"):
        token_id = get_auth_token(base_url, login, password, 600, domain)
        assert token_id, "Не удалось получить tockenID"

    with allure.step("Отправка запроса на получение информации об организации"):
        url = f"{base_url}/api/v1/organization/{CREATED_ORGANIZATION_ID}"
        
        allure.attach(
            f"curl -X GET '{url}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token_id}'",
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = requests.get(
            url,
            headers={
                "accept": "application/json",
                "tockenid": token_id
            }
        )
        
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Проверка ответа"):
        assert response.status_code == 200, (
            f"Ошибка при получении информации об организации. "
            f"Status: {response.status_code}, Response: {response.text}"
        )

        organization_data = response.json()
        allure.attach(
            str(organization_data),
            name="Данные организации",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Сравнение данных организации"):
        fields_to_check = [
            "name", "number_contract", "cid", "address", "fact_address",
            "contact_name", "contact_data", "contact_phone", "contact_mail",
            "description", "inn", "kpp", "bik", "pay_account", "kor_account",
            "bank_name", "sub_right_ref_id", "manager_id", "tenant_id",
            "type_right_ref_id"
        ]

        comparison_results = []
        for field in fields_to_check:
            expected = str(CREATED_ORGANIZATION_DATA.get(field))
            actual = str(organization_data.get(field))
            match = expected == actual
            comparison_results.append({
                "field": field,
                "expected": expected,
                "actual": actual,
                "match": match
            })
            
            assert match, (
                f"Поле {field} не соответствует ожидаемому значению. "
                f"Ожидалось: {expected}, Получено: {actual}"
            )

        allure.attach(
            str(comparison_results),
            name="Результаты сравнения полей",
            attachment_type=allure.attachment_type.JSON
        )

    with allure.step("Проверка даты начала контракта"):
        contract_time = organization_data.get("contract_begin_time")
        expected_date = CREATED_ORGANIZATION_DATA["contract_begin_time"]
        
        if isinstance(contract_time, dict):
            date_match = contract_time.get("date", "").startswith(expected_date)
        else:
            date_match = str(contract_time).startswith(expected_date)
            
        assert date_match, "Дата начала контракта не соответствует"
        
        allure.attach(
            f"Ожидаемая дата: {expected_date}\n"
            f"Фактическая дата: {contract_time}",
            name="Проверка даты контракта",
            attachment_type=allure.attachment_type.TEXT
        )
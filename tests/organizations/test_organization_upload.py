import os
import time
import pytest
import requests
import allure
from dotenv import load_dotenv
from pathlib import Path
from faker import Faker
from allure_commons.types import AttachmentType

# Инициализация Faker
fake = Faker()

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

# Глобальные переменные для хранения обновленных данных
UPDATED_ORG_DATA = {}

def get_auth_token(login, password, timeoutlive, domain):
    """
    Получение токена аутентификации
    """
    base_url = os.getenv("API_URL")
    login = os.getenv("API_LOGIN")
    password = os.getenv("API_PASSWORD")
    domain = os.getenv("API_DOMAIN")
    url = f"{base_url}/api/v1/token"
    headers = {"accept": "application/json"}
    data = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    
    with allure.step("Отправка запроса для получения токена"):
        allure.attach(str(data), name="Auth Data", attachment_type=AttachmentType.TEXT)
        
        try:
            response = requests.post(url, headers=headers, json=data)
            allure.attach(response.text, name="Response", attachment_type=AttachmentType.TEXT)
            
            if response.status_code == 401:
                pytest.fail(f"Ошибка аутентификации. Проверьте логин/пароль. Ответ сервера: {response.text}")
            
            response.raise_for_status()
            return response.json().get("tokenId")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Ошибка при получении токена: {str(e)}")

@allure.story("Обновление и проверка данных организации")
class TestOrganizationUpdate:
    @classmethod
    def setup_class(cls):
        """Инициализация перед всеми тестами класса"""
        load_dotenv(ENV_FILE)
        
        cls.base_url = os.getenv("API_URL")
        cls.login = os.getenv("API_LOGIN")
        cls.password = os.getenv("API_PASSWORD")
        cls.domain = os.getenv("API_DOMAIN")
        cls.organization_id = os.getenv("ORGANIZATION_ID")
        
        # Проверка обязательных переменных
        missing_vars = []
        if not cls.base_url:
            missing_vars.append("API_URL")
        if not cls.login:
            missing_vars.append("API_LOGIN")
        if not cls.password:
            missing_vars.append("API_PASSWORD")
        if not cls.domain:
            missing_vars.append("API_DOMAIN")
        if not cls.organization_id:
            missing_vars.append("ORGANIZATION_ID")
        
        if missing_vars:
            pytest.fail(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
        
        # Получаем токен один раз для всех тестов
        cls.token = get_auth_token(cls.login, cls.password, 600, cls.domain)

    def test_update_organization(self):
        """Тест обновления данных организации"""
        global UPDATED_ORG_DATA
        
        with allure.step("Генерация тестовых данных для обновления"):
            UPDATED_ORG_DATA = {
                "name": fake.company(),
                "number_contract": str(fake.random_number(digits=10)),
                "address": fake.address().replace('\n', ', '),
                "fact_address": fake.address().replace('\n', ', '),
                "contact_name": fake.name(),
                "contact_data": fake.job(),
                "contact_phone": fake.phone_number(),
                "contact_mail": fake.email(),
                "description": fake.text(max_nb_chars=200),
            }
            allure.attach(str(UPDATED_ORG_DATA), name="Сгенерированные данные", 
                         attachment_type=AttachmentType.JSON)

        with allure.step("Отправка запроса на обновление"):
            update_url = f"{self.base_url}/api/v1/organization/{self.organization_id}"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.put(
                update_url,
                headers=headers,
                json=UPDATED_ORG_DATA,
                timeout=10
            )
            
            allure.attach(str(response.status_code), name="Status Code", attachment_type=AttachmentType.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=AttachmentType.TEXT)

        with allure.step("Проверка ответа"):
            assert response.status_code == 200, f"Ошибка обновления: {response.text}"
            time.sleep(2)  # Краткая пауза для применения изменений

    def test_verify_organization(self):
        """Тест проверки обновленных данных"""
        global UPDATED_ORG_DATA
        
        with allure.step("Запрос данных организации"):
            get_url = f"{self.base_url}/api/v1/organization/{self.organization_id}"
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.get(get_url, headers=headers, timeout=10)
            allure.attach(str(response.status_code), name="Status Code", attachment_type=AttachmentType.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=AttachmentType.TEXT)
            
            assert response.status_code == 200, f"Ошибка запроса: {response.text}"

        with allure.step("Проверка данных"):
            org_data = response.json()
            mismatch = []
            
            for field, expected_value in UPDATED_ORG_DATA.items():
                actual_value = org_data.get(field)
                if actual_value != expected_value:
                    mismatch.append(f"{field}: ожидалось '{expected_value}', получено '{actual_value}'")
            
            assert not mismatch, "Несоответствия в данных:\n" + "\n".join(mismatch)
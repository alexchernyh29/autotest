import os
import pytest
import requests
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.step("Получение токена аутентификации")
def get_auth_token(base_url, login, password, timeoutlive, domain):
    """Получение токена аутентификации"""
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": "******",  # Скрываем пароль в логах
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {"accept": "application/json"}
    
    # Логируем curl команду (без реального пароля)
    allure.attach(
        f"curl -X POST '{url}?login={login}&password=******&timeoutlive={timeoutlive}&domain={domain}' "
        f"-H 'accept: application/json'",
        name="CURL команда для получения токена",
        attachment_type=allure.attachment_type.TEXT
    )
    
    # Отправляем реальный запрос с паролем
    real_params = params.copy()
    real_params["password"] = password
    response = requests.post(url, headers=headers, params=real_params)
    
    allure.attach(
        f"Status Code: {response.status_code}\nResponse: {response.text}",
        name="Ответ сервера",
        attachment_type=allure.attachment_type.TEXT
    )
    
    response.raise_for_status()
    token = response.json().get("tockenID")
    
    if token:
        allure.attach(
            f"Полученный токен (первые 10 символов): {token[:10]}...",
            name="Токен доступа",
            attachment_type=allure.attachment_type.TEXT
        )
    
    return token

@allure.title("Удаление организации")
def test_delete_organization():
    """Тест удаления организации"""
    with allure.step("Подготовка тестовых данных"):
        # Загрузка переменных окружения
        load_dotenv(ENV_FILE)

        # Получение параметров из .env
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        organization_id = os.getenv("ORGANIZATION_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert organization_id, "ORGANIZATION_ID не задан в .env"

    with allure.step("Получение токена авторизации"):
        token_id = get_auth_token(base_url, login, password, 600, domain)
        assert token_id, "Не удалось получить tockenID"

    with allure.step("Формирование запроса на удаление"):
        url = f"{base_url}/api/v1/organization/{organization_id}"
        headers = {
            "accept": "*/*",
            "tockenid": token_id
        }
        
        allure.attach(
            f"curl -X DELETE '{url}' -H 'accept: */*' -H 'tockenid: {token_id}'",
            name="CURL команда для удаления",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Отправка DELETE запроса"):
        response = requests.delete(url, headers=headers)
        
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            name="Ответ сервера на удаление",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Проверка успешного удаления"):
        # Проверка статус-кода (200 или 204 для успешного удаления)
        assert response.status_code in (200, 204), (
            f"Ошибка при удалении организации. "
            f"Status: {response.status_code}, Response: {response.text}"
        )
        
        allure.attach(
            f"Организация {organization_id} удалена. Код ответа: {response.status_code}",
            name="Результат удаления",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Проверка что организация действительно удалена"):
        check_response = requests.get(url, headers=headers)
        
        allure.attach(
            f"Status Code: {check_response.status_code}\nResponse: {check_response.text}",
            name="Проверочный запрос",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert check_response.status_code == 404, (
            "Организация не была удалена, запрос по ID все еще возвращает данные"
        )
        
        allure.attach(
            f"Подтверждение удаления организации {organization_id}. "
            f"Запрос вернул код {check_response.status_code}",
            name="Подтверждение удаления",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Финализация теста"):
        allure.attach(
            f"Организация с ID {organization_id} успешно удалена",
            name="Итоговый результат",
            attachment_type=allure.attachment_type.TEXT
        )
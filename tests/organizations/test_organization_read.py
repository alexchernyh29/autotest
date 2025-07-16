import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

def get_auth_token(login, password, timeoutlive, domain):
    """
    Получение токена аутентификации
    """
    base_url = os.getenv("API_URL")
    login = os.getenv("API_LOGIN")
    password = os.getenv("API_PASSWORD")
    domain = os.getenv("API_DOMAIN")

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

    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status()  # Проверка на ошибки HTTP

    token_data = response.json()
    return token_data.get("tockenID")  # Предполагается, что ответ содержит поле "token"

def test_get_organizations_by_tenant_id():
    """
    Тест получения списка организаций по tenant_id
    Проверяет:
    1. Успешный статус-код (200)
    2. Наличие обязательных полей в ответе
    3. Соответствие запрошенного tenant_id
    """
    # Загрузка переменных окружения
    load_dotenv(ENV_FILE)

    # Получение параметров из .env
    base_url = os.getenv("API_URL")
    login = os.getenv("API_LOGIN")
    password = os.getenv("API_PASSWORD")
    domain = os.getenv("API_DOMAIN")
    test_tenant_id = os.getenv("TEST_TENANT_ID", "123")  # Можно переопределить в .env

    # Проверка обязательных переменных
    assert base_url, "API_URL не задан в .env"
    assert login, "API_LOGIN не задан в .env"
    assert password, "API_PASSWORD не задан в .env"
    assert domain, "API_DOMAIN не задан в .env"

    # Получение токена
    token = get_auth_token(login, password, 600, domain)
    assert token, "Не удалось получить токен"

    # Формирование запроса
    url = f"{base_url}/api/v1/organizations"
    params = {"by_tenant_id": test_tenant_id}
    headers = {
        "accept": "*/*",
        "tockenid": token  # Обратите внимание на опечатку в API (tockenid вместо tokenid)
    }

    # Отправка запроса
    response = requests.get(url, headers=headers, params=params)

    # Проверка статус-кода
    assert response.status_code == 200, (
        f"Ошибка при получении организаций. "
        f"Status: {response.status_code}, Response: {response.text}"
    )

    # Парсинг ответа
    data = response.json()

    # Проверка структуры ответа
    assert isinstance(data, list), "Ответ должен быть списком организаций"

    if data:  # Если организации найдены
        org = data[0]
        assert "id" in org, "Отсутствует поле id в ответе"
        assert "name" in org, "Отсутствует поле name в ответе"
        assert "tenant_id" in org, "Отсутствует поле tenant_id в ответе"
        assert str(org["tenant_id"]) == str(test_tenant_id), (
            f"tenant_id организации ({org['tenant_id']}) "
            f"не соответствует запрошенному ({test_tenant_id})"
        )

    print(f"\nНайдено организаций: {len(data)}")
    print(f"Пример организации: {data[0] if data else 'Нет данных'}")

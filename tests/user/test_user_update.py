import os
import requests
import pytest
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@pytest.mark.run(order=5)
def test_update_user():
    """Обновление данных пользователя с обязательными полями"""
    # Загрузка переменных окружения
    load_dotenv(ENV_FILE)
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")
    test_user_id = os.getenv("CREATED_USER_ID")

    # Проверка наличия обязательных переменных
    assert base_url, "API_URL не задан в .env"
    assert token, "TOKEN_ID не задан в .env"
    assert test_user_id, "CREATED_USER_ID не задан в .env"

    # 1. Сначала получаем текущие данные пользователя
    get_response = requests.get(
        f"{base_url}/api/v1/user/{test_user_id}",
        headers={"tockenid": token, "accept": "*/*"}
    )
    assert get_response.status_code == 200, "Не удалось получить данные пользователя"
    current_data = get_response.json()

    # 2. Подготавливаем данные для обновления
    update_data = {
        "fio": "Новое ФИО",
        "login": current_data["login"],  # Обязательное поле
        "mail": "updated.email@example.com",
        "phone": "79123456789",
        "role_id": current_data["role_id"],  # Обязательное поле из ошибки
        "tenant_id": current_data["tenant_id"],  # Обязательное поле
        "is_manager": 1
    }

    # 3. Отправка запроса на обновление
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "tockenid": token
    }
    
    response = requests.put(
        f"{base_url}/api/v1/user/{test_user_id}",
        headers=headers,
        json=update_data
    )

    # 4. Проверки
    assert response.status_code == 200, f"Ошибка обновления: {response.text}"
    
    # 5. Проверяем, что данные изменились
    updated_response = requests.get(
        f"{base_url}/api/v1/user/{test_user_id}",
        headers={"tockenid": token}
    )
    updated_data = updated_response.json()
    
    assert updated_data["fio"] == update_data["fio"], "ФИО не обновилось"
    assert updated_data["mail"] == update_data["mail"], "Email не обновился"
    assert updated_data["phone"] == update_data["phone"], "Телефон не обновился"
    
    print("\nДанные успешно обновлены:")
    print(f"ID пользователя: {test_user_id}")
    print(f"Новое ФИО: {updated_data['fio']}")
    print(f"Новый email: {updated_data['mail']}")
    print(f"Новый телефон: {updated_data['phone']}")
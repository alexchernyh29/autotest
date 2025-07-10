import os
import requests
from dotenv import load_dotenv, set_key
from pathlib import Path
import pytest
# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@pytest.mark.run(order=6)
def test_delete_user():
    """Удаление пользователя"""
    load_dotenv(ENV_FILE)
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")
    test_user_id = os.getenv("CREATED_USER_ID")

    # Заголовки запроса
    headers = {
        "accept": "*/*",
        "tockenid": token
    }

    # Отправка запроса на удаление
    delete_response = requests.delete(
        f"{base_url}/api/v1/user/{test_user_id}",
        headers=headers
    )

    # Проверка успешного удаления
    assert delete_response.status_code == 200, f"Ошибка удаления: {delete_response.text}"
    
    # Проверка, что пользователь действительно удален
    get_response = requests.get(
        f"{base_url}/api/v1/user/{test_user_id}",
        headers=headers
    )
    assert get_response.status_code == 404, "Пользователь не был удален"
    
    print(f"\nПользователь {test_user_id} успешно удален")
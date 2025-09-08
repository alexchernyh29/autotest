# Удаляет пул ресурсов /api/v1/resource_pool/{id}
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


@allure.story("Удаление пула ресурсов по ID")
def test_delete_resource_pool():
    """
    Тест: удаление существующего пула ресурсов по ID
    Эндпоинт: DELETE /api/v1/resource_pool/{id}
    Проверяет:
      - статус 200 (допускает ответ null)
      - подтверждение удаления через GET-запрос
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        pool_id = os.getenv("POOL_ID")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert pool_id, "POOL_ID не задан в .env"

    try:
        pool_id = int(pool_id)
        assert pool_id > 0, "POOL_ID должен быть положительным числом"
    except (ValueError, TypeError):
        pytest.fail("POOL_ID должен быть целым положительным числом")

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_pool/{pool_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка DELETE-запроса для удаления пула с ID={pool_id}"):
        response = requests.delete(url, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 204:
            with allure.step("Успешно удалено (204 No Content)"):
                assert not response.text.strip(), "Тело ответа должно быть пустым при статусе 204"
        elif response.status_code == 200:
            with allure.step("Успешно удалено (200 OK)"):
                # Допускаем null
                if response.text.strip():
                    try:
                        data = response.json()
                        allure.attach(str(data), name="Response JSON", attachment_type=AttachmentType.JSON)
                        # Опционально: проверяем флаги вроде {"deleted": true}
                        if isinstance(data, dict):
                            assert data.get("deleted") is True or data.get("success") is True or data.get("id") == pool_id
                    except ValueError:
                        pytest.fail("Ответ 200 содержит невалидный JSON")
                else:
                    with allure.step("Ответ 200 с пустым телом — допустимо"):
                        pass
        elif response.status_code == 404:
            pytest.fail(f"Пул с ID={pool_id} не найден. Возможно, он уже удалён.")
        elif response.status_code == 403:
            pytest.fail(f"Доступ запрещён (403). Проверьте права пользователя.")
        else:
            pytest.fail(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    # 🔁 Проверка, что пул действительно удалён
    with allure.step("Подтверждение удаления: GET-запрос должен вернуть 400"):
        get_url = f"{base_url}/api/v1/resource_pool/{pool_id}"
        get_headers = {
            "accept": "application/json",
            "tockenid": token
        }
        verify_response = requests.get(get_url, headers=get_headers)

        allure.attach(
            str(verify_response.status_code),
            name="GET после удаления — статус",
            attachment_type=AttachmentType.TEXT
        )
        allure.attach(
            verify_response.text,
            name="GET после удаления — тело",
            attachment_type=AttachmentType.TEXT
        )

        if verify_response.status_code == 400:
            with allure.step(f"Пул с ID={pool_id} больше не существует — удаление подтверждено"):
                pass
        elif verify_response.status_code == 200:
            pytest.fail(f"Ошибка: пул с ID={pool_id} всё ещё доступен после удаления!")
        else:
            pytest.fail(f"Неожиданный статус при проверке удаления: {verify_response.status_code}")

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Пул с ID={pool_id} успешно удалён и подтверждено отсутствие ресурса.",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
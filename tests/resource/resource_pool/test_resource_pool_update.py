# Обновляет информацию о существующем пуле ресурсов /api/v1/resource_pool/{id}
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


@allure.story("Обновление информации о пуле ресурсов")
def test_update_resource_pool():
    """
    Тест: обновление существующего пула ресурсов по ID
    Эндпоинт: PUT /api/v1/resource_pool/{id}
    Поля: name, description, status_id, service_id, location_id, type_service_id
    Проверяет:
      - статус 200
      - допускает ответ null (если API не возвращает тело)
      - подтверждает изменения через GET-запрос
      - корректность всех вложенных полей
    """
    with allure.step("Загрузка переменных окружения"):
        load_dotenv(ENV_FILE)

    with allure.step("Чтение параметров из .env"):
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        pool_id = os.getenv("POOL_ID")
        name = os.getenv("UPDATE_POOL_NAME", "Обновлённый пул")
        description = os.getenv("UPDATE_POOL_DESCRIPTION", "Обновлённое описание пула")
        status_id = os.getenv("UPDATE_POOL_STATUS_ID", "3")
        service_id = os.getenv("UPDATE_POOL_SERVICE_ID", "416")
        location_id = os.getenv("UPDATE_POOL_LOCATION_ID", "125")
        type_service_id = os.getenv("UPDATE_POOL_TYPE_SERVICE_ID", "1")

    with allure.step("Проверка обязательных переменных окружения"):
        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert pool_id, "POOL_ID не задан в .env"
        assert name.strip(), "UPDATE_POOL_NAME не может быть пустым"

    # Приведение типов
    try:
        pool_id = int(pool_id)
        status_id = int(status_id)
        service_id = int(service_id)
        location_id = int(location_id)
        type_service_id = int(type_service_id)
    except (ValueError, TypeError) as e:
        pytest.fail(f"Ошибка преобразования числовых параметров: {e}")

    assert pool_id > 0, "POOL_ID должен быть положительным"
    assert status_id >= 0, "UPDATE_POOL_STATUS_ID должен быть >= 0"
    assert service_id > 0, "UPDATE_POOL_SERVICE_ID должен быть положительным"
    assert location_id > 0, "UPDATE_POOL_LOCATION_ID должен быть положительным"
    assert type_service_id > 0, "UPDATE_POOL_TYPE_SERVICE_ID должен быть положительным"

    with allure.step("Получение токена аутентификации"):
        token = get_auth_token(login, password, 600, domain)
        assert token, "Не удалось получить токен аутентификации"

    with allure.step("Формирование тела запроса (новые значения)"):
        payload = {
            "name": name,
            "description": description,
            "status_id": status_id,
            "service_id": service_id,
            "location_id": location_id,
            "type_service_id": type_service_id
        }
        allure.attach(str(payload), name="Request Body", attachment_type=AttachmentType.JSON)

    with allure.step("Формирование URL и заголовков"):
        url = f"{base_url}/api/v1/resource_pool/{pool_id}"
        headers = {
            "accept": "application/json",
            "tockenid": token,
            "Content-Type": "application/json"
        }
        allure.attach(url, name="Request URL", attachment_type=AttachmentType.TEXT)
        allure.attach(str(headers), name="Request Headers", attachment_type=AttachmentType.JSON)

    with allure.step(f"Отправка PUT-запроса для обновления пула с ID={pool_id}"):
        response = requests.put(url, json=payload, headers=headers)

        allure.attach(str(response.status_code), name="Response Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.text), name="Response Body", attachment_type=AttachmentType.TEXT)
        allure.attach(str(response.headers), name="Response Headers", attachment_type=AttachmentType.JSON)

    with allure.step("Проверка статуса ответа"):
        if response.status_code == 404:
            pytest.fail(f"Пул с ID={pool_id} не найден. Проверьте корректность ID.")
        elif response.status_code == 400:
            pytest.fail(f"Некорректные данные или ID. Ответ: {response.text}")
        elif response.status_code != 200:
            pytest.fail(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    with allure.step("Парсинг ответа PUT (допускаем null)"):
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(str(data), name="PUT Response Data", attachment_type=AttachmentType.JSON)

        if data is None:
            with allure.step("API вернул null — это допустимо при успешном обновлении"):
                pass
        else:
            with allure.step("API вернул объект — проверим ID"):
                assert isinstance(data, dict), "Ожидался объект или null"
                assert data.get("id") == pool_id, f"ID в ответе ≠ {pool_id}"

    # 🔁 Ключевая проверка: GET после PUT
    with allure.step("Проверка изменений через GET-запрос"):
        get_url = f"{base_url}/api/v1/resource_pool/{pool_id}"
        get_headers = {
            "accept": "application/json",
            "tockenid": token
        }
        get_response = requests.get(get_url, headers=get_headers)

        allure.attach(str(get_response.status_code), name="GET Status Code", attachment_type=AttachmentType.TEXT)
        allure.attach(get_response.text, name="GET Response Body", attachment_type=AttachmentType.TEXT)

        assert get_response.status_code == 200, f"GET запрос провален: {get_response.status_code}"

        try:
            updated = get_response.json()
        except ValueError:
            pytest.fail("GET-ответ не является валидным JSON")

        allure.attach(str(updated), name="Actual Data After Update", attachment_type=AttachmentType.JSON)

        # Проверка корневых полей
        required_fields = ["id", "name", "description", "service_id", "location", "status", "type_service"]
        missing = [field for field in required_fields if field not in updated]
        assert not missing, f"Отсутствуют обязательные поля: {', '.join(missing)}"

        # Проверка ID
        assert updated["id"] == pool_id, f"ID: ожидался {pool_id}, получен {updated['id']}"

        # Проверка обновлённых значений
        assert updated["name"] == name, f"Имя: ожидалось '{name}', получено '{updated['name']}'"
        assert updated["description"] == description, f"Описание: ожидалось '{description}', получено '{updated['description']}'"
        assert updated["service_id"] == service_id, f"service_id: ожидалось {service_id}, получено {updated['service_id']}"

        # location.id
        assert isinstance(updated["location"], dict), "location должно быть объектом"
        assert updated["location"]["id"] == location_id, f"location.id: ожидалось {location_id}, получено {updated['location']['id']}"

        # status.id
        assert isinstance(updated["status"], dict), "status должно быть объектом"
        assert updated["status"]["id"] == status_id, f"status.id: ожидалось {status_id}, получено {updated['status']['id']}"

        # type_service.id
        assert isinstance(updated["type_service"], dict), "type_service должно быть объектом"
        assert updated["type_service"]["id"] == type_service_id, f"type_service.id: ожидалось {type_service_id}, получено {updated['type_service']['id']}"

        # update_time должен быть обновлён
        assert "update_time" in updated, "Отсутствует update_time"
        update_time = updated["update_time"]
        assert isinstance(update_time, dict), "update_time должно быть объектом"
        assert "date" in update_time and isinstance(update_time["date"], str), "update_time.date должно быть строкой"
        assert len(update_time["date"]) >= 19, "update_time.date слишком короткий"

    with allure.step("Тест завершён успешно"):
        allure.attach(
            f"Пул успешно обновлён и проверен: ID={pool_id}, Name='{name}', "
            f"Status ID={status_id}, Location ID={location_id}, Service ID={service_id}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
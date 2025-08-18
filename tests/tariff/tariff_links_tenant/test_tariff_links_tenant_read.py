# Возвращает список связей тарифов с фильтрацией /api/v1/tariff_links_tenant
# tests/tariff/tariff_links_tenant/test_tariff_links_tenant_read.py

import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from allure_commons.types import AttachmentType

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


# Фильтры для параметризации
FILTERS = {
    "by_tenant_id": 123,
    "by_tariff_id": 302,
    "by_service_id": 418,
    "by_location_id": 125
}


@allure.feature("Тарифы")
@allure.story("Фильтрация связей тариф–арендатор")
@pytest.mark.parametrize(
    "filter_key, filter_value",
    [
        ("by_tenant_id", FILTERS["by_tenant_id"]),
        ("by_tariff_id", FILTERS["by_tariff_id"]),
        ("by_service_id", FILTERS["by_service_id"]),
        ("by_location_id", FILTERS["by_location_id"])
    ],
    ids=list(FILTERS.keys())
)
def test_get_tariff_links_tenant_filtered(filter_key, filter_value):
    """
    Параметризованный тест: получение связей тарифов с арендаторами
    по каждому фильтру по отдельности.

    Для каждого фильтра:
    1. Отправляется отдельный GET-запрос
    2. Проверяется, что ВСЕ элементы в ответе соответствуют фильтру
    """
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    # Формируем URL и параметры
    url = f"{base_url}/api/v1/tariff_links_tenant"
    params = {filter_key: filter_value}
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step(f"Отправка GET-запроса с фильтром: {filter_key}={filter_value}"):
        # Генерация cURL
        curl_command = (
            f"curl -X GET '{url}?{filter_key}={filter_value}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(curl_command, name="CURL команда", attachment_type=AttachmentType.TEXT)

        # Логируем параметры и заголовки
        allure.attach(
            json.dumps(params, ensure_ascii=False, indent=2),
            name="Query Parameters",
            attachment_type=AttachmentType.JSON
        )
        allure.attach(
            json.dumps(headers, ensure_ascii=False, indent=2),
            name="Request Headers",
            attachment_type=AttachmentType.JSON
        )

        # Отправка запроса
        response = requests.get(url, params=params, headers=headers)

    with allure.step("Проверка ответа от сервера"):
        final_url = response.url
        allure.attach(final_url, name="Использованный URL", attachment_type=AttachmentType.TEXT)

        status_info = f"Status Code: {response.status_code}"
        response_body = response.text
        full_response = f"{status_info}\nResponse Body:\n{response_body}"

        allure.attach(full_response, name="Response Details", attachment_type=AttachmentType.TEXT)

        assert response.status_code == 200, (
            f"Ожидался статус 200, но получен {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

        assert response.text.strip(), "Ответ от сервера пуст"

        try:
            links = response.json()
        except ValueError as e:
            pytest.fail(f"Ответ не является валидным JSON. Ошибка: {e}\nТело: {response.text}")

        # ✅ Исправление ошибки: преобразуем список в JSON-строку
        allure.attach(
            json.dumps(links, ensure_ascii=False, indent=2),
            name="Response (tariff_links_tenant list)",
            attachment_type=AttachmentType.JSON
        )

        assert isinstance(links, list), "Ожидался массив связей"

        if len(links) == 0:
            allure.attach(
                f"Список пуст при фильтре {filter_key}={filter_value}",
                name="Внимание",
                attachment_type=AttachmentType.TEXT
            )
            pytest.fail(f"Ожидались данные по фильтру {filter_key}={filter_value}, но список пуст")

    with allure.step(f"Проверка, что все элементы соответствуют фильтру: {filter_key}={filter_value}"):
        mismatches = []  # Для сбора несоответствий

        for idx, link in enumerate(links):
            assert isinstance(link, dict), f"Элемент [{idx}] не является объектом"

            # Обязательные поля
            required_fields = ["id", "tariff_id", "tenant_id"]
            missing = [f for f in required_fields if f not in link]
            assert not missing, f"В элементе [{idx}] отсутствуют поля: {missing}"

            tariff = link.get("tariff")
            tenant = link.get("tenant")

            # Проверка соответствия фильтру
            match = False

            if filter_key == "by_tenant_id":
                actual = link.get("tenant_id")
                if actual == filter_value:
                    match = True
                else:
                    mismatches.append(f"[{idx}] tenant_id={actual}, ожидалось {filter_value}")

            elif filter_key == "by_tariff_id":
                actual = link.get("tariff_id")
                if actual == filter_value:
                    match = True
                else:
                    mismatches.append(f"[{idx}] tariff_id={actual}, ожидалось {filter_value}")

            elif filter_key == "by_service_id":
                if (
                    tariff and
                    isinstance(tariff, dict) and
                    "service_id" in tariff and
                    tariff["service_id"] == filter_value
                ):
                    match = True
                else:
                    service_id = tariff.get("service_id") if tariff else None
                    mismatches.append(f"[{idx}] service_id={service_id}, ожидалось {filter_value}")

            elif filter_key == "by_location_id":
                if (
                    tariff and
                    isinstance(tariff, dict) and
                    "location" in tariff and
                    isinstance(tariff["location"], dict) and
                    tariff["location"].get("id") == filter_value
                ):
                    match = True
                else:
                    location_id = tariff.get("location", {}).get("id") if tariff else None
                    mismatches.append(f"[{idx}] location.id={location_id}, ожидалось {filter_value}")

            if not match:
                continue  # Будет обработано далее

        # Финальная проверка
        assert len(mismatches) == 0, (
            f"Найдены элементы, не соответствующие фильтру {filter_key}={filter_value}:\n" +
            "\n".join(mismatches)
        )

    with allure.step("✅ Тест пройден"):
        allure.attach(
            f"Все {len(links)} элементов соответствуют фильтру {filter_key}={filter_value}",
            name="Результат",
            attachment_type=AttachmentType.TEXT
        )
# tests/test_get_tariff_links_organization_filtered.py

import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


# Фильтры для тестирования (по одному)
FILTERS = {
    "by_tenant_id": 123,
    "by_tariff_id": 295,
    "by_name": "ПРИМО РПА_custom_tariff1746023459",
    "by_service_id": 430,
    "by_location_id": 125
}


@allure.feature("Фильтрация связей тарифов с организациями")
@pytest.mark.parametrize(
    "filter_key, filter_value",
    [
        ("by_tenant_id", FILTERS["by_tenant_id"]),
        ("by_tariff_id", FILTERS["by_tariff_id"]),
        ("by_name", FILTERS["by_name"]),
        ("by_service_id", FILTERS["by_service_id"]),
        ("by_location_id", FILTERS["by_location_id"])
    ],
    ids=[
        "by_tenant_id",
        "by_tariff_id",
        "by_name",
        "by_service_id",
        "by_location_id"
    ]
)
def test_get_tariff_links_organization_filtered(filter_key, filter_value):
    """
    Параметризованный тест: получение связей тарифов с организациями
    по каждому фильтру по отдельности.
    """
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    # Формируем фильтр — только один параметр за раз
    params = {filter_key: filter_value}

    url = f"{base_url}/api/v1/tariff_links_organization"
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
        allure.attach(curl_command, "CURL команда", allure.attachment_type.TEXT)

        allure.attach(
            json.dumps(params, ensure_ascii=False, indent=2),
            "Query Parameters",
            allure.attachment_type.JSON
        )

        allure.attach(
            json.dumps(headers, ensure_ascii=False, indent=2),
            "Request Headers",
            allure.attachment_type.JSON
        )

        response = requests.get(url, params=params, headers=headers)

    with allure.step("Проверка ответа"):
        allure.attach(f"Финальный URL: {response.url}", "Использованный URL", allure.attachment_type.TEXT)
        allure.attach(
            f"Status Code: {response.status_code}\nResponse: {response.text}",
            "Response Details",
            allure.attachment_type.TEXT
        )

        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

        try:
            links_list = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(links_list, ensure_ascii=False, indent=2),
            "Response (tariff_links_organization list)",
            allure.attachment_type.JSON
        )

        assert isinstance(links_list, list), "Ожидался массив связей"

        # Проверяем, что хотя бы одна связь соответствует фильтру
        with allure.step("Проверка структуры и соответствия фильтру"):
            if len(links_list) == 0:
                allure.attach(
                    f"Список пуст. Фильтр: {filter_key}={filter_value}",
                    "Внимание",
                    allure.attachment_type.TEXT
                )
                pytest.fail(f"Ожидались данные по фильтру {filter_key}={filter_value}, но список пуст")

            found_match = False
            for link in links_list:
                assert isinstance(link, dict), "Каждая связь должна быть объектом"
                assert "id" in link
                assert "tariff_id" in link
                assert "tenant_id" in link
                assert "name" in link

                # Проверяем соответствие текущему фильтру
                if filter_key == "by_tenant_id" and link["tenant_id"] == filter_value:
                    found_match = True
                elif filter_key == "by_tariff_id" and link["tariff_id"] == filter_value:
                    found_match = True
                elif filter_key == "by_name" and filter_value in str(link["name"]):
                    found_match = True
                elif filter_key == "by_service_id" and "service_id" in link and link["service_id"] == filter_value:
                    found_match = True
                elif filter_key == "by_location_id" and "location_id" in link and link["location_id"] == filter_value:
                    found_match = True

            assert found_match, f"Ни одна из {len(links_list)} связей не соответствует фильтру: {filter_key}={filter_value}"

    with allure.step("✅ Тест пройден"):
        allure.attach(
            f"Найдено {len(links_list)} связей по фильтру {filter_key}={filter_value}",
            "Результат",
            allure.attachment_type.TEXT
        )
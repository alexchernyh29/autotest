# Возвращает список связей тарифов с фильтрацией /api/v1/tariff_links_tenant
# tests/test_get_tariff_links_tenant_filtered.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Фильтрация связей тарифов с арендаторами")
def test_get_tariff_links_tenant_filtered():
    """Получение списка связей тарифов с арендаторами по фильтрам"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"

    # Фильтры из cURL
    filters = {
        "by_tenant_id": 3213,
        "by_tariff_id": 132131,
        "by_service_id": 312131,
        "by_location_id": 132131
    }

    url = f"{base_url}/api/v1/tariff_links_tenant"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step("Формирование и отправка GET-запроса с фильтрами"):
        # Генерация cURL
        curl_command = (
            f"curl -X GET '{url}"
            f"?by_tenant_id={filters['by_tenant_id']}"
            f"&by_tariff_id={filters['by_tariff_id']}"
            f"&by_service_id={filters['by_service_id']}"
            f"&by_location_id={filters['by_location_id']}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(
            curl_command,
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            str(filters),
            name="Query Parameters",
            attachment_type=allure.attachment_type.JSON
        )

        allure.attach(
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

        # Отправка запроса
        response = requests.get(url, params=filters, headers=headers)

        with allure.step("Проверка ответа"):
            allure.attach(
                f"Финальный URL: {response.url}",
                name="Использованный URL",
                attachment_type=allure.attachment_type.TEXT
            )
            allure.attach(
                f"Status Code: {response.status_code}\nResponse: {response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Ожидался статус 200, но получен {response.status_code}"

            try:
                links_list = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                links_list,
                name="Response (tariff_links_tenant list)",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(links_list, list), "Ожидался массив связей (list)"

                if len(links_list) > 0:
                    with allure.step(f"Найдено {len(links_list)} связей по фильтрам"):
                        for link in links_list:
                            assert isinstance(link, dict), "Каждая связь должна быть объектом"
                            assert "id" in link, "Связь должна содержать поле 'id'"
                            assert "tariff_id" in link, "Связь должна содержать поле 'tariff_id'"
                            assert "tenant_id" in link, "Связь должна содержать поле 'tenant_id'"

                            # Проверка, что фильтры соблюдаются
                            if filters.get("by_tenant_id"):
                                assert link["tenant_id"] == filters["by_tenant_id"], \
                                    f"Ожидался tenant_id={filters['by_tenant_id']}, но получен {link['tenant_id']}"

                            if filters.get("by_tariff_id"):
                                assert link["tariff_id"] == filters["by_tariff_id"], \
                                    f"Ожидался tariff_id={filters['by_tariff_id']}, но получен {link['tariff_id']}"

                            # Дополнительные поля
                            # if filters.get("by_service_id"):
                            #     assert link.get("service_id") == filters["by_service_id"], "service_id не совпадает"
                            # if filters.get("by_location_id"):
                            #     assert link.get("location_id") == filters["by_location_id"], "location_id не совпадает"
                else:
                    with allure.step("По заданным фильтрам связи не найдены"):
                        allure.attach(
                            "Список пуст. Это может быть ожидаемым поведением, если нет активных связей.",
                            name="Результат фильтрации",
                            attachment_type=allure.attachment_type.TEXT
                        )
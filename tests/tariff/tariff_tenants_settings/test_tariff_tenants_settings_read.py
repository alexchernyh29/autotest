# Возвращает список настроек тарифов для арендаторов с фильтрацией /api/v1/tariff_tenants_settings?by_tariff_link_organization_id=231312
# tests/test_get_tariff_tenants_settings.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Получение настроек арендатора по связи с организацией")
def test_get_tariff_tenants_settings():
    """Получение списка настроек арендатора по ID связи с организацией"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        link_org_id = os.getenv("CREATED_LINK_ID")  # Используем ID связи из test_create_tariff_link_organization

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert link_org_id, "CREATED_LINK_ID не задан в .env. Сначала создайте связь."

        try:
            link_org_id = int(link_org_id)
        except ValueError:
            pytest.fail("CREATED_LINK_ID должен быть числом")

    url = f"{base_url}/api/v1/tariff_tenants_settings"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    params = {
        "by_tariff_link_organization_id": link_org_id
    }

    with allure.step(f"Отправка GET-запроса на {url} с фильтром by_tariff_link_organization_id={link_org_id}"):
        curl_command = (
            f"curl -X GET '{url}?by_tariff_link_organization_id={link_org_id}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(
            curl_command,
            name="CURL команда",
            attachment_type=allure.attachment_type.TEXT
        )

        allure.attach(
            str(params),
            name="Query Parameters",
            attachment_type=allure.attachment_type.JSON
        )

        allure.attach(
            str(headers),
            name="Request Headers",
            attachment_type=allure.attachment_type.TEXT
        )

        response = requests.get(url, params=params, headers=headers)

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
                settings_list = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                settings_list,
                name="Tenant Settings Response",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры ответа"):
                assert isinstance(settings_list, list), "Ожидался массив настроек (list)"

                if len(settings_list) > 0:
                    with allure.step(f"Найдено {len(settings_list)} настроек для связи ID={link_org_id}"):
                        for setting in settings_list:
                            assert isinstance(setting, dict), "Каждая настройка должна быть объектом"
                            assert "id" in setting, "Настройка должна содержать поле 'id'"
                            assert "tariff_link_organization_id" in setting, \
                                "Настройка должна содержать поле 'tariff_link_organization_id'"
                            assert "setting_key" in setting, "Настройка должна содержать поле 'setting_key'"
                            assert "value" in setting, "Настройка должна содержать поле 'value'"

                            # Проверка соответствия связи
                            assert setting["tariff_link_organization_id"] == link_org_id, \
                                f"Найдена настройка с tariff_link_organization_id={setting['tariff_link_organization_id']}, " \
                                f"ожидался {link_org_id}"
                else:
                    with allure.step(f"У связи ID={link_org_id} нет настроек арендатора"):
                        allure.attach(
                            "Список настроек пуст. Это может быть ожидаемым поведением.",
                            name="Результат",
                            attachment_type=allure.attachment_type.TEXT
                        )
# tests/tariff/tariff_tenants_settings/test_tariff_tenants_settings_read.py

import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv


# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


@allure.feature("Получение настроек арендатора по связи с организацией")
def test_get_tariff_tenants_settings():
    """Получение списка настроек арендатора по ID связи с организацией"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        link_org_id_str = os.getenv("CREATED_LINK_ID", "320")

        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert link_org_id_str, "CREATED_LINK_ID не задан в .env. Сначала создайте связь."

        try:
            link_org_id = int(link_org_id_str)
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

    with allure.step("Проверка HTTP-статуса и формата ответа"):
        allure.attach(f"Финальный URL: {response.url}", "Использованный URL", allure.attachment_type.TEXT)
        allure.attach(
            f"Status Code: {response.status_code}\nResponse Body: {response.text}",
            "Response Details",
            allure.attachment_type.TEXT
        )

        assert response.status_code == 200, f"Ожидался 200, но получен {response.status_code}"

        try:
            settings_list = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(settings_list, ensure_ascii=False, indent=2),
            "Tenant Settings Response",
            allure.attachment_type.JSON
        )

        assert isinstance(settings_list, list), "Ожидался массив настроек"

        if not settings_list:
            with allure.step(f"У связи ID={link_org_id} нет настроек арендатора"):
                allure.attach(
                    "Список настроек пуст. Это может быть ожидаемым поведением.",
                    "Результат",
                    allure.attachment_type.TEXT
                )
            return

    with allure.step(f"Проверка {len(settings_list)} настроек для связи ID={link_org_id}"):
        for idx, setting in enumerate(settings_list):
            with allure.step(f"Настройка #{idx + 1} (ID={setting.get('id')})"):
                assert isinstance(setting, dict), "Каждая настройка должна быть объектом"

                # === Поля на верхнем уровне (реальные, согласно JSON) ===
                required_top_level = [
                    "id",
                    "tariff_setting_id",
                    "tariff_setting",
                    "tariff_link_organization_id",
                    "tariff_link_organization",
                    "tenant_rate_price_active",
                    "tenant_rate_price_passive",
                    "create_time",
                    "update_time",
                    "create_user_id",
                    "update_user_id"
                ]

                missing_top = [field for field in required_top_level if field not in setting]
                assert not missing_top, f"Отсутствуют обязательные поля: {', '.join(missing_top)}"

                # Проверка связи
                assert setting["tariff_link_organization_id"] == link_org_id, \
                    f"tariff_link_organization_id не совпадает: ожидаем {link_org_id}, получен {setting['tariff_link_organization_id']}"

                # Проверка tariff_setting
                tariff_setting = setting["tariff_setting"]
                assert isinstance(tariff_setting, dict), "tariff_setting должен быть объектом"
                assert "id" in tariff_setting, "tariff_setting.id отсутствует"
                assert "tariff_id" in tariff_setting, "tariff_setting.tariff_id отсутствует"


                # Проверка tariff_link_organization
                tariff_link_org = setting["tariff_link_organization"]
                assert isinstance(tariff_link_org, dict), "tariff_link_organization должен быть объектом"
                assert "id" in tariff_link_org, "tariff_link_organization.id отсутствует"
                assert tariff_link_org["id"] == link_org_id, \
                    f"tariff_link_organization.id не совпадает: ожидаем {link_org_id}, получен {tariff_link_org['id']}"

                # Проверка цен
                assert isinstance(setting["tenant_rate_price_active"], (int, float)) and setting["tenant_rate_price_active"] >= 0
                assert isinstance(setting["tenant_rate_price_passive"], (int, float)) and setting["tenant_rate_price_passive"] >= 0

                # Проверка времени
                for time_field in ["create_time", "update_time"]:
                    time_obj = setting[time_field]
                    assert isinstance(time_obj, dict), f"{time_field} должен быть объектом"
                    assert "date" in time_obj, f"{time_field}.date отсутствует"
                    assert "timezone" in time_obj, f"{time_field}.timezone отсутствует"
                    assert "timezone_type" in time_obj, f"{time_field}.timezone_type отсутствует"

                # Проверка ID пользователей
                assert isinstance(setting["create_user_id"], int)
                assert isinstance(setting["update_user_id"], int)

    with allure.step("✅ Все проверки пройдены"):
        allure.attach(
            f"Успешно проверено {len(settings_list)} настроек арендатора для связи с организацией ID={link_org_id}.",
            "Результат",
            allure.attachment_type.TEXT
        )
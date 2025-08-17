import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"

@allure.feature("Получение настроек тарифа")
def test_get_tariffs_settings():
    load_dotenv(ENV_FILE)
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")
    tariff_id_str = os.getenv("CREATED_TARIFF_ID", "304")

    assert base_url, "API_URL не задан в .env"
    assert token, "TOKEN_ID не задан в .env"
    assert tariff_id_str, "CREATED_TARIFF_ID не задан"

    try:
        tariff_id = int(tariff_id_str)
    except ValueError:
        pytest.fail("CREATED_TARIFF_ID должен быть числом")

    url = f"{base_url}/api/v1/tariffs_settings"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }
    params = {"by_tariff_id": tariff_id}

    with allure.step(f"Отправка GET-запроса на {url} с фильтром by_tariff_id={tariff_id}"):
        curl_command = (
            f"curl -X GET '{url}?by_tariff_id={tariff_id}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(curl_command, "CURL команда", allure.attachment_type.TEXT)
        allure.attach(json.dumps(params, ensure_ascii=False, indent=2), "Query Parameters", allure.attachment_type.JSON)
        allure.attach(json.dumps(headers, ensure_ascii=False, indent=2), "Request Headers", allure.attachment_type.JSON)

        response = requests.get(url, params=params, headers=headers)

    with allure.step("Проверка ответа"):
        allure.attach(f"Финальный URL: {response.url}", "Использованный URL", allure.attachment_type.TEXT)
        allure.attach(f"Status Code: {response.status_code}\nResponse: {response.text}", "Response Details", allure.attachment_type.TEXT)

        assert response.status_code == 200

        try:
            settings_list = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(settings_list, ensure_ascii=False, indent=2),
            "Tariff Settings Response",
            allure.attachment_type.JSON
        )

        assert isinstance(settings_list, list), "Ожидался список настроек"
        assert len(settings_list) > 0, f"Не найдено ни одной настройки для tariff_id={tariff_id}"

    with allure.step(f"Проверка каждой из {len(settings_list)} настроек"):
        for idx, setting in enumerate(settings_list):
            with allure.step(f"Проверка настройки #{idx + 1} (id={setting.get('id')})"):
                # Основные поля настройки
                assert "id" in setting
                assert "tariff_id" in setting
                assert "resource_pool_id" in setting
                assert "resource_atom_id" in setting
                assert "resource_value" in setting
                assert "base_price_active" in setting
                assert "base_price_passive" in setting
                assert "time_of_base_price" in setting
                assert "type_state_of_resource" in setting
                assert "type_right_render" in setting

                # Проверка связи с тарифом
                assert setting["tariff_id"] == tariff_id, \
                    f"tariff_id в настройке ({setting['tariff_id']}) не соответствует запрошенному ({tariff_id})"

                # Проверка resource_value — положительное число
                assert isinstance(setting["resource_value"], (int, float)) and setting["resource_value"] > 0

                # base_price_active и passive — неотрицательные числа
                assert isinstance(setting["base_price_active"], (int, float)) and setting["base_price_active"] >= 0
                assert isinstance(setting["base_price_passive"], (int, float)) and setting["base_price_passive"] >= 0
                assert isinstance(setting["time_of_base_price"], int) and setting["time_of_base_price"] > 0

                # Проверка вложенных объектов
                assert "tariff" in setting
                assert "resource_pool" in setting
                assert "resource_atom" in setting

                tariff = setting["tariff"]
                resource_pool = setting["resource_pool"]
                resource_atom = setting["resource_atom"]

                # Проверка tariff
                assert "id" in tariff and tariff["id"] == tariff_id
                assert "name" in tariff and isinstance(tariff["name"], str) and len(tariff["name"].strip()) > 0
                assert "service" in tariff
                assert "status" in tariff
                assert "time_interval" in tariff

                # Проверка service
                service = tariff["service"]
                assert "id" in service
                assert "name" in service and isinstance(service["name"], str)

                # Проверка resource_pool
                assert "id" in resource_pool and resource_pool["id"] == setting["resource_pool_id"]
                assert "name" in resource_pool and isinstance(resource_pool["name"], str)
                assert "location" in resource_pool
                assert "status" in resource_pool

                # Проверка resource_atom
                assert "id" in resource_atom and resource_atom["id"] == setting["resource_atom_id"]
                assert "name" in resource_atom and isinstance(resource_atom["name"], str)
                assert "category" in resource_atom
                category = resource_atom["category"]
                assert "id" in category
                assert "name" in category
                if "unitMeasure" in category:
                    assert "id" in category["unitMeasure"]
                    assert "name" in category["unitMeasure"]
                if "typeRef" in category:
                    assert "id" in category["typeRef"]
                    assert "name" in category["typeRef"]

                # Проверка create/update time (формат)
                for field in ["create_time", "update_time"]:
                    assert field in setting, f"Отсутствует {field} в настройке"
                    time_obj = setting[field]
                    assert isinstance(time_obj, dict)
                    assert "date" in time_obj
                    assert "timezone" in time_obj
                    assert "timezone_type" in time_obj

                # Проверка create/update user_id
                assert isinstance(setting["create_user_id"], int)
                assert isinstance(setting["update_user_id"], int)

    with allure.step("✅ Все проверки пройдены"):
        allure.attach(
            f"Успешно получено и проверено {len(settings_list)} настроек тарифа {tariff_id}.",
            "Результат",
            allure.attachment_type.TEXT
        )
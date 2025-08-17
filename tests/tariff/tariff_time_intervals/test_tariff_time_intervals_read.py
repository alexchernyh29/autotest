import os
import json
import requests
import pytest
import allure
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

@allure.feature("Получение временных интервалов тарифов")
def test_get_tariff_time_intervals():
    load_dotenv(ENV_FILE)
    base_url = os.getenv("API_URL")
    token = os.getenv("TOKEN_ID")

    assert base_url, "API_URL не задан в .env"
    assert token, "TOKEN_ID не задан в .env"

    url = f"{base_url}/api/v1/tariff_time_intervals"
    headers = {
        "accept": "application/json",
        "tockenid": token
    }

    with allure.step(f"Отправка GET-запроса на {url}"):
        curl_command = (
            f"curl -X GET '{url}' "
            f"-H 'accept: application/json' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(curl_command, "CURL команда", allure.attachment_type.TEXT)
        allure.attach(json.dumps(headers, ensure_ascii=False, indent=2), "Request Headers", allure.attachment_type.JSON)

        response = requests.get(url, headers=headers)

    with allure.step("Проверка ответа"):
        allure.attach(f"Status Code: {response.status_code}\nResponse: {response.text}", "Response Details", allure.attachment_type.TEXT)

        assert response.status_code == 200

        try:
            intervals = response.json()
        except ValueError:
            pytest.fail("Ответ не является валидным JSON")

        allure.attach(
            json.dumps(intervals, ensure_ascii=False, indent=2),
            "Tariff Time Intervals List",
            allure.attachment_type.JSON
        )

        assert isinstance(intervals, list)
        assert len(intervals) > 0, "Список временных интервалов пуст"

        expected_sysnames = {"second", "minute", "hour", "day", "month", "year"}
        found_sysnames = set()

        for interval in intervals:
            assert isinstance(interval, dict)
            assert "id" in interval
            assert "name" in interval
            assert "sysname" in interval

            interval_id = interval["id"]
            interval_name = interval["name"]
            interval_sysname = interval["sysname"]

            assert isinstance(interval_id, int) and interval_id > 0
            assert isinstance(interval_name, str) and len(interval_name.strip()) > 0
            assert isinstance(interval_sysname, str) and len(interval_sysname.strip()) > 0

            found_sysnames.add(interval_sysname)

        # Проверяем, что все ожидаемые интервалы присутствуют
        assert expected_sysnames.issubset(found_sysnames), \
            f"Ожидались интервалы: {expected_sysnames}, найдены: {found_sysnames}"
# get organization report/api/v1/report_organization/320?report_type=Services&begin_date=01.01.2024&end_date=30.01.2024
# tests/report/test_report_organization_services.py

import os
import requests
import pytest
import allure
from dotenv import load_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

@allure.feature("Отчёты по организациям")
def test_get_services_report_for_organization():
    """Получение отчёта по услугам для организации за период"""
    with allure.step("Подготовка тестовых данных"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        token = os.getenv("TOKEN_ID")
        org_id = os.getenv("TEST_ORGANIZATION_ID", "320")  # Можно задать в .env

        # Проверка обязательных переменных
        assert base_url, "API_URL не задан в .env"
        assert token, "TOKEN_ID не задан в .env"
        assert org_id, "TEST_ORGANIZATION_ID не задан в .env и не передан"

        try:
            org_id = int(org_id)
        except ValueError:
            pytest.fail("TEST_ORGANIZATION_ID должен быть числом")

    url = f"{base_url}/api/v1/report_organization/{org_id}"
    headers = {
        "accept": "*/*",
        "tockenid": token
    }

    # Параметры запроса
    params = {
        "report_type": "Services",
        "begin_date": "01.01.2024",
        "end_date": "30.01.2024"
    }

    with allure.step(f"Отправка GET-запроса на {url} с параметрами"):
        # Генерация cURL
        curl_command = (
            f"curl -X GET '{url}"
            f"?report_type={params['report_type']}"
            f"&begin_date={params['begin_date']}"
            f"&end_date={params['end_date']}' "
            f"-H 'accept: */*' "
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
                report_data = response.json()
            except ValueError:
                pytest.fail("Ответ не является валидным JSON")

            allure.attach(
                report_data,
                name="Report Data",
                attachment_type=allure.attachment_type.JSON
            )

            with allure.step("Проверка структуры отчёта"):
                assert isinstance(report_data, dict), "Ожидался объект с данными отчёта"

                # Проверка обязательных полей
                assert "organization_id" in report_data, "В ответе отсутствует organization_id"
                assert "report_type" in report_data, "В ответе отсутствует report_type"
                assert "begin_date" in report_data, "В ответе отсутствует begin_date"
                assert "end_date" in report_data, "В ответе отсутствует end_date"
                assert "services" in report_data, "В ответе отсутствует список услуг"

                # Проверка значений
                assert report_data["organization_id"] == org_id, \
                    f"Ожидалась организация ID={org_id}, но получен {report_data['organization_id']}"

                assert report_data["report_type"] == params["report_type"], \
                    f"Тип отчёта не совпадает: ожидаем {params['report_type']}, получено {report_data['report_type']}"

                assert report_data["begin_date"] == params["begin_date"], "begin_date не совпадает"
                assert report_data["end_date"] == params["end_date"], "end_date не совпадает"

                services = report_data["services"]
                assert isinstance(services, list), "Поле 'services' должно быть массивом"

                if len(services) > 0:
                    with allure.step(f"Найдено {len(services)} услуг в отчёте"):
                        for service in services:
                            assert "service_id" in service, "Услуга должна содержать service_id"
                            assert "name" in service, "Услуга должна содержать name"
                            assert "quantity" in service, "Услуга должна содержать quantity"
                            assert "unit" in service, "Услуга должна содержать unit"
                            assert "cost" in service, "Услуга должна содержать cost"
                else:
                    with allure.step("Список услуг пуст"):
                        allure.attach(
                            "В отчёте нет данных об услугах за указанный период.",
                            name="Результат",
                            attachment_type=allure.attachment_type.TEXT
                        )
# tests/report/test_report_read.py

import os
import json
import requests
import pytest
import allure
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Путь к .env файлу
ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"


def get_auth_token(login: str, password: str, timeoutlive: int, domain: str) -> str:
    """Получение токена аутентификации через API"""
    base_url = os.getenv("API_URL")
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {"accept": "application/json"}

    with allure.step("🔐 Получение токена аутентификации"):
        allure.attach(f"URL: {url}", "Request URL", allure.attachment_type.TEXT)
        allure.attach(json.dumps(params, indent=2, ensure_ascii=False), "Request Params", allure.attachment_type.JSON)
        allure.attach(json.dumps(headers, indent=2, ensure_ascii=False), "Request Headers", allure.attachment_type.JSON)

        try:
            response = requests.post(url, headers=headers, params=params, timeout=10)
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)
            allure.attach(response.text, "Response Body", allure.attachment_type.TEXT)
            response.raise_for_status()

            token_data = response.json()
            tocken_id = token_data.get("tockenID")
            if not tocken_id:
                raise KeyError("Поле 'tockenID' отсутствует в ответе API")

            allure.attach(tocken_id, "✅ Успешно получен tockenID", allure.attachment_type.TEXT)
            return tocken_id

        except Exception as e:
            allure.attach(str(e), "❌ Ошибка запроса", allure.attachment_type.TEXT)
            pytest.fail(f"❌ Не удалось получить токен: {e}")


@allure.feature("Отчёты по организациям")
def test_get_services_report_for_organization():
    """Получение отчёта по услугам для организации (ORGANIZATION_ID из .env) за последние 6 месяцев"""
    with allure.step("🔧 Подготовка тестовых данных из .env"):
        load_dotenv(ENV_FILE)

        base_url = os.getenv("API_URL")
        org_id_str = os.getenv("ORGANIZATION_ID")

        login = os.getenv("API_LOGIN")        
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        timeoutlive = int(os.getenv("TOKEN_TIMEOUT", 3600))

        assert base_url, "❌ API_URL не задан в .env"
        assert org_id_str, "❌ ORGANIZATION_ID не задан в .env"
        assert login, "❌ API_LOGIN не задан в .env"
        assert password, "❌ API_PASSWORD не задан в .env"
        assert domain, "❌ API_DOMAIN не задан в .env"

        try:
            org_id = int(org_id_str)
        except ValueError:
            pytest.fail(f"❌ ORGANIZATION_ID должен быть числом, получено: {org_id_str}")

        allure.attach(
            f"API_URL: {base_url}\n"
            f"ORGANIZATION_ID: {org_id}\n"
            f"API_LOGIN: {login}\n"
            f"DOMAIN: {domain}",
            "📋 Загруженные данные",
            allure.attachment_type.TEXT
        )

    end_date = datetime.now()
    begin_date = end_date - timedelta(days=6 * 30)

    formatted_begin = begin_date.strftime("%d.%m.%Y")
    formatted_end = end_date.strftime("%d.%m.%Y")

    with allure.step("📅 Расчёт периода отчёта"):
        date_info = f"""
        Начало: {formatted_begin}
        Конец: {formatted_end}
        """
        allure.attach(date_info, "🗓 Рассчитанные даты", allure.attachment_type.TEXT)

    with allure.step("🔑 Получение токена через API"):
        token = get_auth_token(login, password, timeoutlive, domain)
        assert token, "❌ Токен не был получен"

    # 📥 Формируем запрос
    url = f"{base_url}/api/v1/report_organization/{org_id}"
    headers = {
        "accept": "*/*",
        "tockenid": token
    }
    params = {
        "report_type": "Services",
        "begin_date": formatted_begin,
        "end_date": formatted_end
    }

    with allure.step(f"📤 Отправка GET-запроса к {url}"):
        curl_command = (
            f"curl -X GET '{url}"
            f"?report_type={params['report_type']}"
            f"&begin_date={params['begin_date']}"
            f"&end_date={params['end_date']}' "
            f"-H 'accept: */*' "
            f"-H 'tockenid: {token}'"
        )
        allure.attach(curl_command, "📎 CURL команда", allure.attachment_type.TEXT)
        allure.attach(json.dumps(params, indent=2, ensure_ascii=False), "🔍 Query Parameters", allure.attachment_type.JSON)
        allure.attach(json.dumps(headers, indent=2, ensure_ascii=False), "📡 Request Headers", allure.attachment_type.JSON)

        response = requests.get(url, params=params, headers=headers)

    with allure.step("📥 Получен ответ от сервера"):
        allure.attach(f"🔗 Финальный URL: {response.url}", "🌐 Использованный URL", allure.attachment_type.TEXT)
        allure.attach(
            f"🔢 Status Code: {response.status_code}\n\n📄 Response Body:\n{response.text}",
            "📦 Raw Response",
            allure.attachment_type.TEXT
        )

        assert response.status_code == 200, f"❌ Ожидался 200, получен {response.status_code}"

        try:
            report_data = response.json()
        except ValueError:
            pytest.fail("❌ Ответ не является валидным JSON")

        allure.attach(
            json.dumps(report_data, ensure_ascii=False, indent=2),
            "📊 Полный ответ API",
            allure.attachment_type.JSON
        )

    with allure.step("✅ Валидация структуры отчёта"):
        assert isinstance(report_data, dict), "Ответ должен быть объектом"
        assert "header" in report_data, "❌ Отсутствует 'header' в ответе"
        assert "items" in report_data, "❌ Отсутствует 'items' в ответе"

        header = report_data["header"]
        assert isinstance(header, dict), "header должен быть объектом"
        assert "$organization" in header, "❌ Отсутствует $organization в header"

        org_info = header["$organization"]
        assert "id" in org_info, "❌ Отсутствует id в $organization"
        response_org_id = org_info["id"]

        with allure.step(f"🆔 Проверка ID организации: ожидаем {org_id}, получено {response_org_id}"):
            assert response_org_id == org_id, \
                f"❌ ID организации не совпадает: ожидаем {org_id}, получено {response_org_id}"

            allure.attach(
                json.dumps(org_info, ensure_ascii=False, indent=2),
                "🏢 Данные организации",
                allure.attachment_type.JSON
            )

        assert "begin_date" in header, "❌ Отсутствует begin_date в header"
        assert "end_date" in header, "❌ Отсутствует end_date в header"

        assert header["begin_date"] == formatted_begin, \
            f"❌ begin_date не совпадает: ожидаем {formatted_begin}, получено {header['begin_date']}"

        assert header["end_date"] == formatted_end, \
            f"❌ end_date не совпадает: ожидаем {formatted_end}, получено {header['end_date']}"

        items = report_data["items"]
        assert isinstance(items, list), "items должен быть списком"

        if items:
            with allure.step(f"✅ Найдено {len(items)} услуг(и)"):
                for i, item in enumerate(items):
                    with allure.step(f"Услуга #{i + 1}"):
                        assert "service_id" in item
                        assert "name" in item
                        assert "quantity" in item
                        assert "unit" in item
                        assert "cost" in item
                    if i == 0:
                        allure.attach(
                            json.dumps(item, ensure_ascii=False, indent=2),
                            "📄 Пример услуги (первый элемент)",
                            allure.attachment_type.JSON
                        )
        else:
            with allure.step("🟡 Список услуг пуст"):
                allure.attach(
                    "За указанный период услуги не найдены.",
                    "Результат",
                    allure.attachment_type.TEXT
                )
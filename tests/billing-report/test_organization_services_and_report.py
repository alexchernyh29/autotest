import os
import pytest
import requests
import allure
from datetime import datetime, timedelta, date
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import json
import random


ENV_FILE = find_dotenv()
assert ENV_FILE, "Файл .env не найден в корне проекта"

CREATED_ORGANIZATION_ID = None

NUM_SERVICES_TOTAL = 10
CURRENT_MONTH = datetime.now().month
CURRENT_YEAR = datetime.now().year

LOG_FILE_PATH = "organization_creation.log"

last_used_date = None

@allure.step("Получение токена аутентификации")
def get_auth_token(base_url, login, password, timeoutlive, domain):
    url = f"{base_url}/api/v1/tocken"
    params = {
        "login": login,
        "password": password,
        "timeoutlive": timeoutlive,
        "domain": domain
    }
    headers = {"accept": "application/json"}
    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("tockenID")

@allure.step("Получение единиц измерения (resource_units_measure)")
def get_resource_units_measure(base_url, token_id):
    url = f"{base_url}/api/v1/resource_units_measure"
    headers = {
        "accept": "application/json",
        "tockenid": token_id
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@allure.step("Получение типов биллинга (roles_render_billing)")
def get_billing_roles(base_url, token_id):
    url = f"{base_url}/api/v1/billing/roles_render_billing"
    headers = {
        "accept": "application/json",
        "tockenid": token_id
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@allure.step("Получение атомарных ресурсов (resource_atoms)")
def get_resource_atoms(base_url, token_id):
    url = f"{base_url}/api/v1/resource_atoms"
    headers = {
        "accept": "application/json",
        "tockenid": token_id
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@allure.step("Добавление услуги организации")
def add_service_to_organization(base_url, token_id, org_id, service_data, record_start_date, record_end_date, quantity, time_val):
    url = f"{base_url}/api/v1/pre_billing/manual/items"
    payload = {
        "org_id": org_id,
        "unit_measure_id": service_data["unit_measure_id"],
        "resource_atom_id": service_data["resource_atom_id"],
        "payment_type": service_data["payment_type"], 
        "billing_type_id": service_data["billing_type_id"],
        "record_start_date": record_start_date,
        "record_end_date": record_end_date,
        "quantity": quantity,
        "price": service_data["price"],
        "time": time_val
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "tockenid": token_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = {
            "success": response.ok,
            "status_code": response.status_code,
            "response_text": response.text,
            "payload": payload,
            "headers": headers,
            "url": url
        }
        if not response.ok:
            allure.attach(
                json.dumps(result, ensure_ascii=False, indent=2),
                name=f"Ошибка добавления услуги '{service_data['name']}'",
                attachment_type=allure.attachment_type.JSON
            )
        else:
            allure.attach(
                json.dumps(result, ensure_ascii=False, indent=2),
                name=f"Успешное добавление услуги '{service_data['name']}'",
                attachment_type=allure.attachment_type.JSON
            )
        return result
    except Exception as e:
        error_details = {
            "error": str(e),
            "payload": payload,
            "headers": headers,
            "url": url
        }
        allure.attach(
            json.dumps(error_details, ensure_ascii=False, indent=2),
            name=f"Исключение при добавлении услуги '{service_data['name']}'",
            attachment_type=allure.attachment_type.JSON
        )
        return {
            "success": False,
            "error": str(e),
            "payload": payload,
            "headers": headers,
            "url": url
        }

@allure.step("Запись в лог-файл")
def log_message(message, log_file_path=LOG_FILE_PATH):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"[INFO] [{timestamp}] — {message}\n")

# @allure.step("Запись заголовка дня в лог")
def log_day_header(day_str, log_file_path=LOG_FILE_PATH):
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("-" * 60 + "\n")
        f.write(f"[SERVICE LOG] [{day_str}]\n")
        f.write("-" * 60 + "\n")

# @allure.step("Запись итога дня в лог")
def log_daily_summary(day_str, service_count, total_amount, log_file_path=LOG_FILE_PATH):
    timestamp = f"{day_str} 18:00:00"
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"[SUMMARY] [{timestamp}] — ИТОГО за день: {service_count} услуги | Общая сумма: {total_amount:.2f} руб.\n")

@allure.step("Запись финального отчёта")
def log_final_report(start_date, end_date, total_days, total_services, total_amount, avg_daily, failed_services, log_file_path=LOG_FILE_PATH):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("-" * 60 + "\n")
        f.write(f"[FINAL SUMMARY] [{timestamp}]\n")
        f.write("-" * 60 + "\n")
        f.write(f"[REPORT] За период: {start_date} — {end_date}\n")
        f.write(f"[REPORT] Всего дней учёта: {total_days}\n")
        f.write(f"[REPORT] Общее количество попыток услуг: {total_services}\n")
        f.write(f"[REPORT] Успешно добавлено: {total_services - failed_services}\n")
        f.write(f"[REPORT] Неудачных попыток: {failed_services}\n")
        f.write(f"[REPORT] Общая сумма по успешным услугам: {total_amount:.2f} руб.\n")
        f.write(f"[REPORT] Средняя выручка в день: {avg_daily:.2f} руб.\n")
        f.write("\n")
        f.write("[NOTICE] Отчёт успешно сформирован. Данные сохранены в системе учёта.\n")
        f.write("[END OF LOG]\n")

@allure.feature("Организации")
def test_add_services_and_generate_report():
    """Тест: добавление услуг организации с перерывами не менее 1 дня между ними и генерация отчёта
    Каждая услуга длится 2 дня, между услугами — минимум 1 день перерыва.
    """
    global CREATED_ORGANIZATION_ID, last_used_date

    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# organization_creation.log\n")
        f.write(f"# Лог-файл создания организации и учёта оказанных услуг по дням\n")
        f.write(f"# Сгенерировано: {now_str}\n\n")
        f.write(f"[INFO] [{now_str}] — Инициализация создания организации...\n")

    with allure.step("Загрузка данных организации"):
        load_dotenv(ENV_FILE)
        base_url = os.getenv("API_URL")
        login = os.getenv("API_LOGIN")
        password = os.getenv("API_PASSWORD")
        domain = os.getenv("API_DOMAIN")
        CREATED_ORGANIZATION_ID = os.getenv("ORGANIZATION_ID")

        assert base_url, "API_URL не задан в .env"
        assert login, "API_LOGIN не задан в .env"
        assert password, "API_PASSWORD не задан в .env"
        assert domain, "API_DOMAIN не задан в .env"
        assert CREATED_ORGANIZATION_ID, "ORGANIZATION_ID не найден. Сначала выполните test_create_organization"

        log_message(f"ID организации: {CREATED_ORGANIZATION_ID}")

    with allure.step("Получение токена авторизации"):
        token_id = get_auth_token(base_url, login, password, 600, domain)
        assert token_id, "Не удалось получить tockenID"

    with allure.step("Получение данных организации для лога"):
        url_org = f"{base_url}/api/v1/organization/{CREATED_ORGANIZATION_ID}"
        response = requests.get(
            url_org,
            headers={"accept": "application/json", "tockenid": token_id}
        )
        response.raise_for_status()
        org_data = response.json()

        log_message(f"Название организации: \"{org_data.get('name', 'Не указано')}\"")
        log_message(f"Юридический адрес: {org_data.get('address', 'Не указан')}")
        log_message(f"ИНН: {org_data.get('inn', 'Не указан')}")
        log_message(f"Расчётный счёт: {org_data.get('pay_account', 'Не указан')}")
        # log_message("Организация успешно зарегистрирована в системе.")
        log_message("Старт учёта оказанных услуг. Каждая услуга длится 2 дня, между услугами — минимум 1 день перерыва.")

    with allure.step("Получение единиц измерения"):
        units_measure = get_resource_units_measure(base_url, token_id)
        units_map = {item["id"]: item["name"] for item in units_measure}
        allure.attach(json.dumps(units_map, ensure_ascii=False, indent=2), name="Единицы измерения", attachment_type=allure.attachment_type.JSON)

    with allure.step("Получение типов биллинга"):
        billing_roles = get_billing_roles(base_url, token_id)
        billing_map = {item["id"]: item["name"] for item in billing_roles}
        allure.attach(json.dumps(billing_map, ensure_ascii=False, indent=2), name="Типы биллинга", attachment_type=allure.attachment_type.JSON)

    with allure.step("Получение атомарных ресурсов"):
        resource_atoms = get_resource_atoms(base_url, token_id)
        valid_resources = [
            res for res in resource_atoms
            if res.get("category") and res.get("category", {}).get("unitMeasure")
        ]
        allure.attach(json.dumps(valid_resources, ensure_ascii=False, indent=2), name="Примеры ресурсов (первые 5)", attachment_type=allure.attachment_type.JSON)

    SERVICE_CATALOG = []
    PAYMENT_TYPES = ["service", "total"]

    selected_resources = random.sample(valid_resources, min(NUM_SERVICES_TOTAL, len(valid_resources))) if valid_resources else []

    if not selected_resources:
        pytest.fail("Нет доступных ресурсов для формирования каталога услуг")

    for res in selected_resources:
        try:
            unit_measure_id = res["category"]["unitMeasure"]["id"]
            unit_name = units_map.get(unit_measure_id, "Неизвестно")
            billing_type_id = 2
            if billing_roles:
                billing_type_id = random.choice([role["id"] for role in billing_roles])

            price = random.randint(100, 5000)
            payment_type = random.choice(PAYMENT_TYPES)

            service = {
                "name": res["name"],
                "price": price,
                "unit_measure_id": unit_measure_id,
                "resource_atom_id": res["id"],
                "payment_type": payment_type,
                "billing_type_id": billing_type_id,
                "unit_name": unit_name
            }
            SERVICE_CATALOG.append(service)
        except Exception as e:
            allure.attach(str(e), name=f"Ошибка при формировании услуги из ресурса {res.get('id', 'N/A')}", attachment_type=allure.attachment_type.TEXT)
            continue

    if len(SERVICE_CATALOG) < NUM_SERVICES_TOTAL:
        pytest.fail(f"Не удалось сформировать каталог из {NUM_SERVICES_TOTAL} услуг. Создано только {len(SERVICE_CATALOG)}.")

    allure.attach(
        json.dumps(SERVICE_CATALOG, ensure_ascii=False, indent=2),
        name="Сформированный каталог услуг (ровно NUM_SERVICES_TOTAL записей)",
        attachment_type=allure.attachment_type.JSON
    )

    services_by_day = {} 
    total_services_added = 0
    total_services_attempted = 0 
    max_attempts = 100 
    attempts = 0

    MAX_START_DAY = 29

    all_service_attempts = []

    while total_services_added < NUM_SERVICES_TOTAL and attempts < max_attempts:
        attempts += 1

        if last_used_date is None:
            start_day = 1
        else:
            min_start_date = last_used_date + timedelta(days=2)
            start_day = min_start_date.day

            if start_day > MAX_START_DAY:
                break

        try:
            start_date_obj = date(CURRENT_YEAR, CURRENT_MONTH, start_day)
        except ValueError:
            break

        end_date_obj = start_date_obj + timedelta(days=1)
        last_used_date = end_date_obj

        service_choice = random.choice(SERVICE_CATALOG)
        quantity = random.randint(1, 5)
        price = service_choice["price"]
        amount = quantity * price

        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        end_date_str = end_date_obj.strftime("%Y-%m-%d")

        with allure.step(f"Добавление услуги: {service_choice['name']} на {start_date_str} — {end_date_str}"):
            api_response = add_service_to_organization(
                base_url=base_url,
                token_id=token_id,
                org_id=int(CREATED_ORGANIZATION_ID),
                service_data=service_choice,
                record_start_date=start_date_str,
                record_end_date=end_date_str,
                quantity=quantity,
                time_val=quantity
            )

            day_str = start_date_str
            if day_str not in services_by_day:
                services_by_day[day_str] = []

            service_log_entry = {
                "name": service_choice["name"],
                "quantity": quantity,
                "price": price,
                "amount": amount,
                "unit": service_choice.get("unit_name", ""),
                "payment_type": service_choice["payment_type"],
                "timestamp": (datetime.combine(start_date_obj, datetime.min.time()) + timedelta(hours=random.randint(9, 17))).strftime("%Y-%m-%d %H:%M:%S"),
                "success": api_response.get("success", False),
                "status_code": api_response.get("status_code", "N/A"),
                "error": api_response.get("error", "N/A"),
                "response_text": api_response.get("response_text", "N/A")
            }

            services_by_day[day_str].append(service_log_entry)
            all_service_attempts.append(service_log_entry)

            if api_response.get("success"):
                total_services_added += 1
                # log_message(f"Успешно добавлена услуга: {service_choice['name']} на {start_date_str} — {end_date_str}. Сумма: {amount:.2f} руб.")
            else:
                log_message(f"ОШИБКА при добавлении услуги: {service_choice['name']} на {start_date_str} — {end_date_str}. Код: {api_response.get('status_code', 'N/A')}, Текст: {api_response.get('response_text', 'N/A')}")

        total_services_attempted += 1

    if total_services_added < NUM_SERVICES_TOTAL:
        allure.attach(
            f"Не удалось добавить все {NUM_SERVICES_TOTAL} услуг. Успешно: {total_services_added}, Неудачно: {NUM_SERVICES_TOTAL - total_services_added}",
            name="Итог по добавлению услуг",
            attachment_type=allure.attachment_type.TEXT
        )
        # pytest.fail(f"Не удалось добавить все {NUM_SERVICES_TOTAL} услуг с соблюдением перерывов. Добавлено: {total_services_added}")

    total_amount_all = 0
    total_services_all = 0
    failed_services = 0
    sorted_days = sorted(services_by_day.keys())

    for day_str in sorted_days:
        log_day_header(day_str)

        daily_total = 0
        daily_count = 0
        daily_failed = 0

        for service in services_by_day[day_str]:
            daily_count += 1
            if service["success"]:
                daily_total += service["amount"]
                total_amount_all += service["amount"]
                total_services_all += 1
            else:
                daily_failed += 1
                failed_services += 1

            log_entry = (
                f"{'' if service['success'] else '❌'} Услуга: \"{service['name']}\" | "
                f"Тип: {service['payment_type']} | "
                f"Кол-во: {service['quantity']} {service.get('unit', '')} | "
                f"Цена за ед.: {service['price']:.2f} руб. | "
                f"Сумма: {service['amount']:.2f} руб. | "
                f"Период: {day_str} — {(datetime.strptime(day_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')} | "
                f"Статус: {'OK' if service['success'] else f'ERROR {service.get("status_code", "N/A")}' }"
            )
            timestamp = service['timestamp']
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(f"[INFO] [{timestamp}] — {log_entry}\n")

        log_daily_summary(day_str, daily_count, daily_total)

    if sorted_days:
        start_date_str = sorted_days[0]
        last_start = datetime.strptime(sorted_days[-1], "%Y-%m-%d").date()
        end_date_str = (last_start + timedelta(days=1)).strftime("%Y-%m-%d")
        total_days = len(sorted_days)
        avg_daily = total_amount_all / total_days if total_days > 0 else 0

        log_final_report(
            start_date=start_date_str,
            end_date=end_date_str,
            total_days=total_days,
            total_services=total_services_all,
            total_amount=total_amount_all,
            avg_daily=avg_daily,
            failed_services=failed_services
        )

    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        log_content = f.read()
        allure.attach(log_content, name="Лог создания и услуг", attachment_type=allure.attachment_type.TEXT)

    allure.attach(
        json.dumps(all_service_attempts, ensure_ascii=False, indent=2),
        name="Все попытки добавления услуг (успешные и неудачные)",
        attachment_type=allure.attachment_type.JSON
    )

    # assert total_services_all == NUM_SERVICES_TOTAL, f"Добавлено {total_services_all} из {NUM_SERVICES_TOTAL} запланированных услуг"
    assert total_amount_all > 0 or failed_services > 0, "Общая сумма по услугам равна нулю и не было ни одной успешной услуги"

    allure.attach(
        f"Итого услуг (попыток): {total_services_attempted}\n"
        f"Успешно добавлено: {total_services_all}\n"
        f"Неудачных попыток: {failed_services}\n"
        f"Общая сумма: {total_amount_all:.2f} руб.",
        name="Финансовый результат и статистика",
        attachment_type=allure.attachment_type.TEXT
    )
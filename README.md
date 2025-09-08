```markdown
# API Autotests

## 📋 Требования

- Python 3.11+ (рекомендуется 3.11.4)
- Git 2.40+
- Доступ к API autotest

## 🛠️ Установка

### 1. Установите Python

[Скачайте Python](https://www.python.org/downloads/) и установите с опцией:
```

[✓] Add Python to PATH

````

Проверьте установку:
```bash
python --version
pip --version
````

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

Если файла нет, установите пакеты вручную:

```bash
pip install requests pytest python-dotenv allure-pytest
```

## ⚙️ Настройка окружения

1. Создайте файл `.env` в корне проекта:

```ini
API_URL=your_url
API_LOGIN=your_login
API_PASSWORD=your_password
TOKEN_TIMEOUT=600
API_DOMAIN=domen
TOKEN_ID=
```

2. Добавьте `.env` в `.gitignore`:

```bash
echo ".env" >> .gitignore
```

## 🚀 Запуск тестов

### Основные команды

```bash
# Все тесты
pytest tests/ -v

# Конкретный тест
pytest tests/test_auth.py -v

# С генерацией отчета Allure
pytest --alluredir=allure-results
allure serve allure-results
```

### Параметризованный запуск

```bash
# Только smoke-тесты
pytest -m smoke

# С выводом логов
pytest -v --capture=no
```

## 📁 Структура проекта

```
autotest/
├── tests/
│   ├── organizations/            # Тесты для организаций
│   │   ├── test_organization_create.py
│   │   ├── test_organization_delete.py
│   │   ├── test_organization_read.py
│   │   ├── test_organization_update.py
│   │   └── test_organizations_read.py
│   │
│   ├── pre-billing_items/        # Предварительный биллинг: элементы
│   │   ├── test_pre-billing_items_create.py
│   │   ├── test_pre-billing_items_delete.py
│   │   ├── test_pre-billing_items_read.py
│   │   └── test_pre-billing_items_update.py
│   │
│   ├── pre-billing_manual/       # Мануальные расчёты биллинга
│   │   ├── test_pre-billing_manual_create.py
│   │   ├── test_pre-billing_manual_delete.py
│   │   ├── test_pre-billing_manual_list.py
│   │   ├── test_pre-billing_manual_read.py
│   │   └── test_pre-billing_manual_update.py
│   │
│   ├── pre-billing_organizations/ # Организации в предбиллинге
│   │   ├── test_pre-billing_organizations_create.py
│   │   ├── test_pre-billing_organizations_delete.py
│   │   ├── test_pre-billing_organizations_read.py
│   │   └── test_pre-billing_organizations_update.py
│   │
│   ├── pre-billing_reports/      # Отчёты предварительного биллинга
│   │   ├── test_pre-billing_reports_atom_total.py
│   │   ├── test_pre-billing_reports_ip_address.py
│   │   └── test_pre-billing_reports_total.py
│   │
│   ├── pre-billing_resource/     # Ресурсы в предбиллинге
│   │   ├── test_pre-billing_resource_create.py
│   │   ├── test_pre-billing_resource_delete.py
│   │   ├── test_pre-billing_resource_items.py
│   │   ├── test_pre-billing_resource_read.py
│   │   └── test_pre-billing_resource_update.py
│   │
│   ├── report/                   # Общие отчёты
│   │   └── test_report_read.py
│   │
│   ├── resource/                 # Управление ресурсами
│   │   ├── category_types/
│   │   │   └── test_category_types_read.py
│   │   │
│   │   ├── resource_atom/
│   │   │   ├── test_resource_atom_create.py
│   │   │   ├── test_resource_atom_delete.py
│   │   │   ├── test_resource_atom_read.py
│   │   │   └── test_resource_atom_update.py
│   │   │
│   │   ├── resource_atoms/
│   │   │   └── test_resource_atoms_read.py
│   │   │
│   │   ├── resource_category_ref/
│   │   │   ├── test_resource_category_ref_create.py
│   │   │   ├── test_resource_category_ref_delete.py
│   │   │   ├── test_resource_category_ref_list.py
│   │   │   ├── test_resource_category_ref_read.py
│   │   │   └── test_resource_category_ref_update.py
│   │   │
│   │   ├── resource_location/
│   │   │   ├── test_resource_location_create.py
│   │   │   ├── test_resource_location_delete.py
│   │   │   ├── test_resource_location_read.py
│   │   │   └── test_resource_location_update.py
│   │   │
│   │   ├── resource_locations/
│   │   │   └── test_resource_locations_list.py
│   │   │
│   │   ├── resource_pool/
│   │   │   ├── test_resource_pool_create.py
│   │   │   ├── test_resource_pool_delete.py
│   │   │   ├── test_resource_pool_read.py
│   │   │   └── test_resource_pool_update.py
│   │   │
│   │   ├── resource_pools/
│   │   │   └── test_resource_pools_read.py
│   │   │
│   │   ├── resource_pool_link_atom/
│   │   │   ├── test_resource_pool_link_atom_create.py
│   │   │   ├── test_resource_pool_link_atom_delete.py
│   │   │   ├── test_resource_pool_link_atom_read.py
│   │   │   └── test_resource_pool_link_atom_update.py
│   │   │
│   │   ├── resource_service/
│   │   │   ├── test_resource_service_create.py
│   │   │   ├── test_resource_service_delete.py
│   │   │   ├── test_resource_service_read.py
│   │   │   └── test_resource_service_update.py
│   │   │
│   │   ├── resource_services/
│   │   │   └── test_resource_services_read.py
│   │   │
│   │   ├── resource_types_ref/
│   │   │   └── test_resource_types_ref_read.py
│   │   │
│   │   ├── resource_units_measure/
│   │   │   ├── test_resource_units_measure_create.py
│   │   │   ├── test_resource_units_measure_delete.py
│   │   │   ├── test_resource_units_measure_list.py
│   │   │   ├── test_resource_units_measure_read.py
│   │   │   └── test_resource_units_measure_update.py
│   │   │
│   │   └── type_services/
│   │       └── test_type_services_read.py
│   │
│   ├── role/                     # Роли пользователей
│   │   ├── test_role_read_id.py
│   │   └── test_role_read_list.py
│   │
│   ├── service/                  # Сервисы и их параметры
│   │   ├── roles_render_billing/
│   │   │   └── test_roles_render_billing_read.py
│   │   │
│   │   ├── services/
│   │   │   └── test_services_read.py
│   │   │
│   │   ├── services_parameters_copy/
│   │   │   ├── test_services_parameters_copy.py
│   │   │   └── test_services_parameters_copy_read.py
│   │   │
│   │   ├── service_crud/
│   │   │   ├── test_service_create.py
│   │   │   ├── test_service_delete.py
│   │   │   ├── test_service_read.py
│   │   │   └── test_service_update.py
│   │   │
│   │   ├── service_history/
│   │   │   └── test_service_history_read.py
│   │   │
│   │   ├── service_operation/
│   │   │   └── test_service_operation_read.py
│   │   │
│   │   ├── service_parametrs_history/
│   │   │   └── test_service_parametrs_history_read.py
│   │   │
│   │   ├── service_paramets/
│   │   │   ├── test_service_paramets_create.py
│   │   │   ├── test_service_paramets_delete.py
│   │   │   ├── test_service_paramets_read.py
│   │   │   └── test_service_paramets_update.py
│   │   │
│   │   ├── service_pool_link_atom/
│   │   │   ├── test_service_pool_link_atom_read.py
│   │   │   └── test_service_pool_link_atom_update.py
│   │   │
│   │   ├── service_pool_link_atoms/
│   │   │   └── test_service_pool_link_atoms_read.py
│   │   │
│   │   ├── service_pool_link_atom_history/
│   │   │   ├── test_service_pool_link_atom_history_create.py
│   │   │   ├── test_service_pool_link_atom_history_delete.py
│   │   │   ├── test_service_pool_link_atom_history_read.py
│   │   │   └── test_service_pool_link_atom_history_update.py
│   │   │
│   │   ├── user_group_billing_service/
│   │   │   ├── test_user_group_billing_service_create.py
│   │   │   ├── test_user_group_billing_service_delete.py
│   │   │   ├── test_user_group_billing_service_read.py
│   │   │   └── test_user_group_billing_service_update.py
│   │   │
│   │   ├── user_group_make_billing_service/
│   │   │   ├── test_user_group_make_billing_service_create.py
│   │   │   └── test_user_group_make_billing_service_read.py
│   │   │
│   │   └── vmw/
│   │       └── test_vmw_read.py
│   │
│   ├── tariff/                   # Тарифы и настройки
│   │   ├── tariffs/
│   │   │   └── test_tariffs_read.py
│   │   │
│   │   ├── tariffs_settings/
│   │   │   └── test_tariffs_settings_read.py
│   │   │
│   │   ├── tariff_crud/
│   │   │   ├── test_tariff_create.py
│   │   │   ├── test_tariff_delete.py
│   │   │   ├── test_tariff_read.py
│   │   │   └── test_tariff_update.py
│   │   │
│   │   ├── tariff_links_organization/
│   │   │   └── test_tariff_links_organization_read.py
│   │   │
│   │   ├── tariff_links_tenant/
│   │   │   └── test_tariff_links_tenant_read.py
│   │   │
│   │   ├── tariff_link_organization_crud/
│   │   │   ├── test_tariff_link_organization_create.py
│   │   │   ├── test_tariff_link_organization_delete.py
│   │   │   ├── test_tariff_link_organization_read.py
│   │   │   └── test_tariff_link_organization_update.py
│   │   │
│   │   ├── tariff_link_tenant_crud/
│   │   │   ├── test_tariff_link_tenant_create.py
│   │   │   ├── test_tariff_link_tenant_delete.py
│   │   │   └── test_tariff_link_tenant_read.py
│   │   │
│   │   ├── tariff_setting_types/
│   │   │   └── test_tariff_setting_types_read.py
│   │   │
│   │   ├── tariff_tenants_settings/
│   │   │   └── test_tariff_tenants_settings_read.py
│   │   │
│   │   ├── tariff_tenant_settings_crud/
│   │   │   ├── test_tariff_tenant_settings_create.py
│   │   │   ├── test_tariff_tenant_settings_delete.py
│   │   │   ├── test_tariff_tenant_settings_read.py
│   │   │   └── test_tariff_tenant_settings_update.py
│   │   │
│   │   └── tariff_time_intervals/
│   │       └── test_tariff_time_intervals_read.py
│   │
│   ├── token/                    # Авторизация и токены
│   │   └── test_auth.py
│   │
│   ├── user/                     # Тесты с пользователями
│   │   ├── test_user_create.py
│   │   ├── test_user_crud.py
│   │   ├── test_user_delete.py
│   │   ├── test_user_read.py
│   │   └── test_user_update.py
│   │
│   └── users/                    # Тесты действия с пользователями
│       ├── test_users_add_org.py
│       ├── test_users_org.py
│       └── test_users_read.py
│
├── helpers/                      # Вспомогательные модули
│   ├── api_client.py             # Клиент API (GET, POST, PUT, DELETE)
│   ├── models.py                 # Pydantic модели для запросов и ответов
│   └── utils.py                  # Утилиты: генерация данных, валидаторы, логирование
│
├── config/                       # Конфигурация окружения
│   └── config.py                 # Параметры: URL, headers, базовые данные
│
├── .env                          # Переменные окружения (не в git)
├── .gitignore                    # Игнорируемые файлы
├── requirements.txt              # Зависимости (pytest, requests, pydantic и т.д.)
├── pytest.ini                    # Настройка pytest
└── README.md                     # Документация проекта
```

## 🔧 CI/CD (GitHub Actions)

Пример файла `.github/workflows/tests.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --alluredir=allure-results
      - name: Upload Allure report
        uses: actions/upload-artifact@v3
        with:
          name: allure-report
          path: allure-results
```

## 🛠️ Дополнительные инструменты

### Генерация отчетов

```bash
# HTML отчет
pytest --html=report.html

# Allure отчет (требуется Java 8+)
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### Виртуальное окружение

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

## 📞 Поддержка

При проблемах:

1. Проверьте `.env` файл
2. Запустите с параметром `--capture=no`
3. Откройте Issue в репозитории

```

### Особенности этого README:
1. **Пошаговая установка** Python и зависимостей
2. **Настройка окружения** с примером `.env`
3. **Команды для запуска** с разными опциями
4. **CI/CD пример** для GitHub Actions
5. **Структура проекта** в виде дерева
6. **Дополнительные инструменты** для отчетов
```

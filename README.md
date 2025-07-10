Вот готовый `README.md` для вашего проекта автотестов на Python с подробными инструкциями по настройке:

```markdown
# CorpSoft API Autotests

Проект автотестов для API CorpSoft на Python

## 📋 Требования

- Python 3.11+ (рекомендуется 3.11.4)
- Git 2.40+
- Доступ к API CorpSoft

## 🛠️ Установка

### 1. Установите Python
[Скачайте Python](https://www.python.org/downloads/) и установите с опцией:
```
[✓] Add Python to PATH
```

Проверьте установку:
```bash
python --version
pip --version
```

### 2. Клонируйте репозиторий
```bash
git clone git@github.com:alexchernyh29/corpsoft.git
cd corpsoft
```

### 3. Установите зависимости
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
API_URL=https://dev1api.cloudpanel.ru
API_LOGIN=your_login
API_PASSWORD=your_password
TOKEN_TIMEOUT=600
API_DOMAIN=cloudpanel.ru
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
corpsoft/
├── tests/               # Тесты
│   ├── test_auth.py     # Тесты авторизации
│   └── test_users.py    # Тесты пользователей
├── helpers/            # Вспомогательные модули
│   ├── api_client.py   # Клиент для API
│   └── models.py       # Модели данных
├── .env                # Конфигурация (не в git)
├── .gitignore          # Игнорируемые файлы
└── README.md           # Эта документация
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
          python-version: '3.11'
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

Для использования:
1. Сохраните как `README.md` в корне проекта
2. Обновите данные API в секции "Настройка окружения"
3. При необходимости добавьте свои теги (например, `@pytest.mark.smoke`)

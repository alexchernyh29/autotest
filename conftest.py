import pytest


def pytest_collection_modifyitems(items):
    """
    Изменяем порядок выполнения тестов:
    1. Аутентификация
    2. Пользователи
    3. Организации
    4. Связи пользователей и организаций
    5. Роли
    6. Отчёты
    7. Ресурсы
    8. Тарифы
    9. Остальные тесты
    """
    ordered_items = []

    # 1. Тесты аутентификации
    ordered_items.extend([i for i in items if "token/test_auth" in i.nodeid])

    # 2. Тесты пользователей
    ordered_items.extend([i for i in items if "user/test_user_create" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_read" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_update" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_delete" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_crud" in i.nodeid])

    # 3. Тесты организаций
    ordered_items.extend([i for i in items if "organizations/test_organization_create" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organization_read" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organization_upload" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organization_delete" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organizations_read" in i.nodeid])

    # 4. Тесты связей пользователей и организаций
    ordered_items.extend([i for i in items if "users/test_users_add_org" in i.nodeid])
    ordered_items.extend([i for i in items if "users/test_users_org" in i.nodeid])
    ordered_items.extend([i for i in items if "users/test_users_read" in i.nodeid])

    # 5. Тесты ролей
    ordered_items.extend([i for i in items if "role/" in i.nodeid and i not in ordered_items])

    # 6. Тесты отчётов
    ordered_items.extend([i for i in items if "report/" in i.nodeid and i not in ordered_items])

    # 7. Тесты ресурсов
    ordered_items.extend([i for i in items if "resource/" in i.nodeid and i not in ordered_items])

    # 8. Тесты тарифов
    ordered_items.extend([i for i in items if "tariff/" in i.nodeid and i not in ordered_items])

    # 9. Все остальные тесты (на всякий случай)
    remaining = [i for i in items if i not in ordered_items]
    ordered_items.extend(remaining)

    # Обновляем порядок
    items[:] = ordered_items
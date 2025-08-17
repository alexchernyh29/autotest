# conftest.py

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
    7. Ресурсы (resource_service в порядке CRUD)
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

    # 7. Тесты resource_service — строгий порядок CRUD
    resource_service_path = "resource_service/"
    
    create_tests = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_create" in i.nodeid]
    read_tests = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_read" in i.nodeid]
    update_tests = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_update" in i.nodeid]
    delete_tests = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_delete" in i.nodeid]

    ordered_items.extend(create_tests)
    ordered_items.extend(read_tests)
    ordered_items.extend(update_tests)
    ordered_items.extend(delete_tests)

    # 8. Остальные тесты ресурсов (если есть, например, /resource/ без _service)
    other_resource_tests = [i for i in items if "resource/" in i.nodeid and i not in ordered_items]
    ordered_items.extend(other_resource_tests)

    # 9. Тесты тарифов
    tariff_tests = [i for i in items if "tariff/" in i.nodeid and i not in ordered_items]
    ordered_items.extend(tariff_tests)

    # 10. Все остальные тесты
    remaining = [i for i in items if i not in ordered_items]
    ordered_items.extend(remaining)

    # Обновляем порядок
    items[:] = ordered_items
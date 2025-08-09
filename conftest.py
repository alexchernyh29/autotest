import pytest

def pytest_collection_modifyitems(items):
    """Изменяем порядок выполнения тестов"""
    ordered_items = []
    
    # 1. Тесты аутентификации
    ordered_items.extend([i for i in items if "token/test_auth" in i.nodeid])
    
    # 2. Тесты пользователей
    ordered_items.extend([i for i in items if "user/test_user_create" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_read" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_update" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_delete" in i.nodeid])
    ordered_items.extend([i for i in items if "user/test_user_crud" in i.nodeid])
    # ... остальные тесты пользователей
    
    # 3. Тесты организаций
    ordered_items.extend([i for i in items if "organizations/test_organization_create" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organization_read" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organization_upload" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organization_delete" in i.nodeid])
    ordered_items.extend([i for i in items if "organizations/test_organizations_read" in i.nodeid])
    # ... остальные тесты организаций

    # 3. Тесты пользователей организаций
    ordered_items.extend([i for i in items if "users/test_users_org" in i.nodeid])
    ordered_items.extend([i for i in items if "users/test_users_read" in i.nodeid])

    # 5. Тесты тарифов
    
    
    items[:] = ordered_items
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
    7. Ресурсы: resource_service (CRUD)
    8. Ресурсы: resource_atom (CRUD)
    9. Остальные ресурсы
    10. Тарифы
    11. Остальные тесты
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
    role_tests = [i for i in items if "role/" in i.nodeid and i not in ordered_items]
    ordered_items.extend(role_tests)

    # 6. Тесты отчётов
    report_tests = [i for i in items if "report/" in i.nodeid and i not in ordered_items]
    ordered_items.extend(report_tests)

    # 7. Тесты resource_service — CRUD порядок
    resource_service_path = "resource_service/"
    create_rs = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_create" in i.nodeid]
    read_rs = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_read" in i.nodeid]
    update_rs = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_update" in i.nodeid]
    delete_rs = [i for i in items if resource_service_path in i.nodeid and "test_resource_service_delete" in i.nodeid]

    ordered_items.extend(create_rs)
    ordered_items.extend(read_rs)
    ordered_items.extend(update_rs)
    ordered_items.extend(delete_rs)

    # 8. Тесты resource_atom — CRUD порядок
    resource_atom_path = "resource_atom/"
    create_ra = [i for i in items if resource_atom_path in i.nodeid and "test_create_resource_atom" in i.nodeid]
    read_ra = [i for i in items if resource_atom_path in i.nodeid and "test_get_resource_atom_by_id" in i.nodeid]
    update_ra = [i for i in items if resource_atom_path in i.nodeid and "test_update_resource_atom" in i.nodeid]
    delete_ra = [i for i in items if resource_atom_path in i.nodeid and "test_delete_resource_atom_by_id" in i.nodeid]

    ordered_items.extend(create_ra)
    ordered_items.extend(read_ra)
    ordered_items.extend(update_ra)
    ordered_items.extend(delete_ra)

    # 9. Тесты resource_atom — CRUD порядок
    resource_location_path = "resource_location/"
    create_rl = [i for i in items if resource_location_path in i.nodeid and "test_resource_location_create" in i.nodeid]
    read_rl = [i for i in items if resource_location_path in i.nodeid and "test_resource_location_read" in i.nodeid]
    update_rl = [i for i in items if resource_location_path in i.nodeid and "test_resource_location_update" in i.nodeid]
    delete_rl = [i for i in items if resource_location_path in i.nodeid and "test_resource_location_delete" in i.nodeid]

    ordered_items.extend(create_rl)
    ordered_items.extend(read_rl)
    ordered_items.extend(update_rl)
    ordered_items.extend(delete_rl)

    # 10. Тесты resource_atom — CRUD порядок
    resource_category_path = "resource_category_ref/"
    create_rc = [i for i in items if resource_category_path in i.nodeid and "test_resource_category_ref_create" in i.nodeid]
    read_rc = [i for i in items if resource_category_path in i.nodeid and "test_resource_category_ref_read" in i.nodeid]
    update_rc = [i for i in items if resource_category_path in i.nodeid and "test_resource_category_ref_update" in i.nodeid]
    delete_rc = [i for i in items if resource_category_path in i.nodeid and "test_resource_category_ref_delete" in i.nodeid]
    list_rc = [i for i in items if resource_category_path in i.nodeid and "test_resource_category_ref_list" in i.nodeid]

    ordered_items.extend(create_rc)
    ordered_items.extend(read_rc)
    ordered_items.extend(update_rc)
    ordered_items.extend(delete_rc)
    ordered_items.extend(list_rc)

    # 11. Остальные тесты ресурсов (например, /resource/, /resource_pools/ и т.д.)
    other_resource_tests = [
        i for i in items 
        if ("resource/" in i.nodeid or "resource_pools" in i.nodeid) 
        and i not in ordered_items
    ]
    ordered_items.extend(other_resource_tests)

    # 13. Тесты тарифов
    # tariff_crud
    ordered_items.extend([i for i in items if "tariff/tariff_crud/test_tariff_create" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_crud/test_tariff_read" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_crud/test_tariff_update" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_crud/test_tariff_delete" in i.nodeid])
    # tariff_link_organization_crud
    ordered_items.extend([i for i in items if "tariff/tariff_link_organization_crud/test_tariff_link_organization_create" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_link_organization_crud/test_tariff_link_organization_read" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_link_organization_crud/test_tariff_link_organization_update" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_link_organization_crud/test_tariff_link_organization_delete" in i.nodeid])
    # tariff_link_tenant_crud
    ordered_items.extend([i for i in items if "tariff/tariff_link_tenant_crud/test_tariff_link_tenant_create" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_link_tenant_crud/test_tariff_link_tenant_read" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_link_tenant_crud/test_tariff_link_tenant_delete" in i.nodeid])
    # tariff_links_organization
    ordered_items.extend([i for i in items if "tariff/tariff_links_organization/test_tariff_links_organization_read" in i.nodeid])
    # tariff_links_tenant
    ordered_items.extend([i for i in items if "tariff/tariff_links_tenant/test_tariff_links_tenant_read" in i.nodeid])
    # tariff_setting_types
    ordered_items.extend([i for i in items if "tariff/tariff_setting_types/test_tariff_setting_types_read" in i.nodeid])
    # tariff_tenant_settings_crud
    ordered_items.extend([i for i in items if "tariff/tariff_tenant_settings_crud/test_tariff_tenant_settings_create" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_tenant_settings_crud/test_tariff_tenant_settings_read" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_tenant_settings_crud/test_tariff_tenant_settings_update" in i.nodeid])
    ordered_items.extend([i for i in items if "tariff/tariff_tenant_settings_crud/test_tariff_tenant_settings_delete" in i.nodeid])
    # tariff_tenants_settings
    ordered_items.extend([i for i in items if "tariff/tariff_tenants_settings/test_tariff_tenants_settings_read" in i.nodeid])
    # tariff_time_intervals
    ordered_items.extend([i for i in items if "tariff/tariff_time_intervals/test_tariff_time_intervals_read" in i.nodeid])
    # tariffs
    ordered_items.extend([i for i in items if "tariff/tariffs/test_tariffs_read" in i.nodeid])
    # tariffs_settings
    ordered_items.extend([i for i in items if "tariff/tariffs_settings/test_tariffs_settings_read" in i.nodeid])

    # 14. Все остальные тесты
    remaining = [i for i in items if i not in ordered_items]
    ordered_items.extend(remaining)

    # Применяем порядок
    items[:] = ordered_items
def test_sql_schema_table_count() -> None:
    from tests.test_final_project_static import test_schema_has_at_least_twenty_tables

    test_schema_has_at_least_twenty_tables()


def test_sql_schema_keys() -> None:
    from tests.test_final_project_static import test_core_tables_have_primary_keys_and_foreign_keys

    test_core_tables_have_primary_keys_and_foreign_keys()

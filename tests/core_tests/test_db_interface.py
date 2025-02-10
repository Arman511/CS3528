import pytest
from abc import ABC
import os
import sys

# flake8: noqa: F811

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from core.database_interface import DatabaseInterface


class MockDatabaseInterface(DatabaseInterface, ABC):
    def connect(self, connection, database):
        self.connection = connection
        self.database = database

    def get_all(self, table):
        return []

    def get_one_by_id(self, table, id_val):
        return None

    def insert(self, table, data):
        return True

    def update_one_by_id(self, table, id_val, data):
        return True

    def update_one_by_field(self, table, field, value, data):
        return True

    def delete_by_id(self, table, id_val):
        return True

    def delete_all(self, table):
        return True

    def increment(self, table, id_val, field, increment):
        return True

    def delete_one_by_field(self, table, field, value):
        return True

    def get_by_email(self, table, email):
        return None

    def get_one_by_field(self, table, field, value):
        return None

    def is_table(self, table):
        return table in self.table_list

    def get_all_by_two_fields(self, table, field1, value1, field2, value2):
        return []

    def get_all_by_in_list(self, table, field, values_list):
        return []

    def update_by_field(self, table, field, value, data):
        return True

    def get_all_by_field(self, table, field, value):
        return []

    def create_index(self, table, field):
        return True

    def get_all_by_text_search(self, table, search_text):
        return []

    def delete_all_by_field(self, table, field, value):
        return True


@pytest.fixture
def db_interface():
    return MockDatabaseInterface()


def test_setup(db_interface):
    assert db_interface is not None


def test_add_table(db_interface):
    db_interface.add_table("users")
    assert "users" in db_interface.get_tables()


def test_is_table(db_interface):
    db_interface.add_table("orders")
    assert db_interface.is_table("orders") is True
    assert db_interface.is_table("non_existing") is False

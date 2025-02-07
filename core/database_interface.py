from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    def __init__(self):
        self.connection = None
        self.database = None
        self.table_list = []

    def add_table(self, table):
        self.table_list.append(table)

    @abstractmethod
    def connect(self, connection, database):
        pass

    @abstractmethod
    def get_all(self, table):
        pass

    @abstractmethod
    def get_one_by_id(self, table, id_val):
        pass

    @abstractmethod
    def insert(self, table, data):
        pass

    @abstractmethod
    def update_one_by_id(self, table, id_val, data):
        pass

    @abstractmethod
    def update_one_by_field(self, table, field, value, data):
        pass

    @abstractmethod
    def delete_by_id(self, table, id_val):
        pass

    @abstractmethod
    def delete_all(self, table):
        pass

    @abstractmethod
    def increment(self, table, id_val, field, increment):
        pass

    @abstractmethod
    def delete_one_by_field(self, table, field, value):
        pass

    @abstractmethod
    def get_by_email(self, table, email):
        pass

    @abstractmethod
    def get_one_by_field(self, table, field, value):
        pass

    @abstractmethod
    def is_table(self, table):
        pass

    @abstractmethod
    def get_all_by_two_fields(self, table, field1, value1, field2, value2):
        pass

    @abstractmethod
    def get_all_by_in_list(self, table, field, values_list):
        pass

    @abstractmethod
    def update_by_field(self, table, field, value, data):
        pass

    @abstractmethod
    def get_all_by_field(self, table, field, value):
        pass

    @abstractmethod
    def create_index(self, table, field):
        pass

    @abstractmethod
    def get_all_by_list_query(self, table, query):
        pass

    @abstractmethod
    def get_all_by_text_search(self, table, search_text):
        pass

    def get_tables(self):
        return self.table_list

    @abstractmethod
    def delete_all_by_field(self, table, field, value):
        pass

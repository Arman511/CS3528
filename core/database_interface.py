from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    def __init__(self):
        """Initialize the database interface"""
        self.connection = None
        self.database = None
        self.table_list = []

    def add_table(self, table):
        self.table_list.append(table)

    @abstractmethod
    def connect(self, connection, database):
        """Connect to the database"""
        raise NotImplementedError

    @abstractmethod
    def get_all(self, table):
        """Get all the data from the table"""
        raise NotImplementedError

    @abstractmethod
    def get_one_by_id(self, table, id_val):
        """Get one row by id"""
        raise NotImplementedError

    @abstractmethod
    def insert(self, table, data):
        """Insert data into the table"""
        raise NotImplementedError

    @abstractmethod
    def update_one_by_id(self, table, id_val, data):
        """Update one row by id"""
        raise NotImplementedError

    @abstractmethod
    def update_one_by_field(self, table, field, value, data):
        """Update one row by field"""
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self, table, id_val):
        """Delete one row by id"""
        raise NotImplementedError

    @abstractmethod
    def delete_all(self, table):
        """Delete all rows in the table"""
        raise NotImplementedError

    @abstractmethod
    def increment(self, table, id_val, field, increment):
        """Increment a field by a value"""
        raise NotImplementedError

    @abstractmethod
    def delete_one_by_field(self, table, field, value):
        """Delete one row by field"""
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, table, email):
        """Get one row by email"""
        raise NotImplementedError

    @abstractmethod
    def get_one_by_field(self, table, field, value):
        """Get one row by field"""
        raise NotImplementedError

    @abstractmethod
    def is_table(self, table):
        """Check if the table exists"""
        raise NotImplementedError

    @abstractmethod
    def get_all_by_two_fields(self, table, field1, value1, field2, value2):
        """Get all by two fields"""
        raise NotImplementedError

    @abstractmethod
    def get_all_by_in_list(self, table, field, values_list):
        """Get all by in list"""
        raise NotImplementedError

    @abstractmethod
    def update_by_field(self, table, field, value, data):
        """Update by field"""
        raise NotImplementedError

    @abstractmethod
    def get_all_by_field(self, table, field, value):
        """Get all by field"""
        raise NotImplementedError

    @abstractmethod
    def create_index(self, table, field):
        """Create an index"""
        raise NotImplementedError

    @abstractmethod
    def get_all_by_text_search(self, table, search_text):
        """Get all by text search"""
        raise NotImplementedError

    def get_tables(self):
        """Get the list of tables"""
        return self.table_list

    @abstractmethod
    def delete_all_by_field(self, table, field, value):
        """Delete all by field"""
        raise NotImplementedError

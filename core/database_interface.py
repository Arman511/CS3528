class DatabaseInterface:
    def __init__(self):
        self.connection = None
        self.database = None

        self.table_list = []

    def add_table(self, table):
        self.table_list.append(table)

    def connect(self, connection, database):
        raise NotImplementedError

    def get_all(self, table):
        raise NotImplementedError

    def get_one_by_id(self, table, id_val):
        raise NotImplementedError

    def insert(self, table, data):
        raise NotImplementedError

    def update_one_by_id(self, table, id_val, data):
        raise NotImplementedError

    def update_one_by_field(self, table, field, value, data):
        raise NotImplementedError

    def delete_by_id(self, table, id_val):
        raise NotImplementedError

    def delete_all(self, table):
        raise NotImplementedError

    def get_tables(self):
        return self.table_list

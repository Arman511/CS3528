class DatabaseInterface:
    def __init__(self):
        self.connection = None
        self.database = None

        self.table_list = []

    def add_table(self, table):
        self.table_list.append(table)

    def connect(self):
        raise NotImplementedError

    def get_all(self, table):
        raise NotImplementedError

    def get_one_by_id(self, table, id):
        raise NotImplementedError

    def insert(self, table, data):
        raise NotImplementedError

    def update(self, table, id, data):
        raise NotImplementedError

    def delete_by_id(self, table, id):
        raise NotImplementedError

    def delete_all(self, table):
        raise NotImplementedError

    def get_tables(self):
        return self.table_list

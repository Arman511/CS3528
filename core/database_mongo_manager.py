import pymongo
from .database_interface import DatabaseInterface

class DatabaseMongoManager(DatabaseInterface):

    def __init__(self, connection, database):
        super().__init__()

        self.connection = self.connect(connection)

    def connect(self, connection=None, database=None):
        self.connection = pymongo.MongoClient(connection)
        self.database = self.connection["database"]

    def get_all(self, table):
        return self.database[table].find()
    
    def get_one_by_id(self, table, id):
        return self.database[table].find_one({"_id": id})
    
    def insert(self, table, data):
        return self.database[table].insert_one(data)
    
    def update(self, table, id, data):
        return self.database[table].update_one({"_id": id}, {"$set": data})
    
    def increment(self, table, id, field, increment):
        return self.database[table].update_one({"_id": id}, {"$inc": {field: increment}})
    
    def delete(self, table, id):
        return self.database[table].delete_one({"_id": id})
    
    def delete_all(self, table):
        return self.database[table].delete_many({})
    
    def get_by_email(self, table, email):
        return self.database[table].find_one({"email": email})
    
    
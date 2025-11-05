from be.model import store
import pymongo

class DBConn:
    def __init__(self):
        self.db = store.get_db_conn()
        self.db["user"].create_index([("user_id", pymongo.ASCENDING)])
        self.db["user_store"].create_index([("user_id", pymongo.ASCENDING), ("store_id", pymongo.ASCENDING)])
        self.db["store"].create_index([("book_id", pymongo.ASCENDING), ("store_id", pymongo.ASCENDING)])

    def user_id_exist(self, user_id):
        result = self.db.user.find_one({"user_id": user_id})
        if result is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        result = self.db.store.find_one({"store_id": store_id, "book_id": book_id})
        if result is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        result = self.db.user_store.find_one({"store_id": store_id})
        if result is None:
            return False
        else:
            return True

from be.model.store import get_db_conn
from pymongo.errors import PyMongoError

class DBConn:
    def __init__(self):
        self.db = get_db_conn()

    def user_id_exist(self, user_id: str) -> bool:
        try:
            return self.db["user"].find_one({"user_id": user_id}) is not None
        except PyMongoError as e:
            print(f"MongoDB 查询 user_id 失败: {e}")
            return False

    def book_id_exist(self, store_id: str, book_id: str) -> bool:
        try:
            return self.db["store"].find_one(
                {"store_id": store_id, "book_id": book_id}
            ) is not None
        except PyMongoError as e:
            print(f"MongoDB 查询 book_id 失败: {e}")
            return False

    def store_id_exist(self, store_id: str) -> bool:
        try:
            return self.db["user_store"].find_one({"store_id": store_id}) is not None
        except PyMongoError as e:
            print(f"MongoDB 查询 store_id 失败: {e}")
            return False
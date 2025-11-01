from be.model import store
from pymongo.errors import PyMongoError

class DBConn:
    def __init__(self):
        try:
            # 从 store 模块获取已初始化的数据库连接 (Database 对象)
            self.db = store.get_db_conn()
        except Exception as e:
            # 记录并保留 None，以便调用方可以检查
            print(f"获取数据库连接失败: {e}")
            self.db = None

    def user_id_exist(self, user_id):
        try:
            return self.db["user"].find_one({"user_id": user_id}) is not None
        except PyMongoError as e:
            print(f"MongoDB 查询 user_id 失败: {e}")
            return False

    def book_id_exist(self, store_id, book_id):
        try:
            return self.db["store"].find_one(
                {"store_id": store_id, "books.book_id": book_id} #嵌套查询匹配
            ) is not None
        except PyMongoError as e:
            print(f"MongoDB 查询 book_id 失败: {e}")
            return False

    def store_id_exist(self, store_id):
        try:
            return self.db["user_store"].find_one({"store_id": store_id}) is not None
        except PyMongoError as e:
            print(f"MongoDB 查询 store_id 失败: {e}")
            return False
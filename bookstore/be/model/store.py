import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import threading


class Store:
    database: str

    def __init__(self,uri="mongodb://localhost:27017/", db_name="bookstore"):
        """
        初始化 MongoDB 数据库连接
        uri: MongoDB 连接地址
        db_name: 数据库名称
        """
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self.init_collections()
            logging.info("MongoDB 已成功连接并初始化数据库。")
        except PyMongoError as e:
            logging.error(f"MongoDB 连接失败: {e}")
            raise

    def init_collections(self):
        collections = [
            "user",
            "user_store",
            "store",
            "new_order",
            "new_order_detail"
        ]
        try:
            #创建用户集合
            self.db.users.create_index([("user_id", 1)], unique=True)
            #创建用户-商店集合
            self.db.user_store.create_index(
            [("user_id", 1), ("store_id", 1)], unique=True
        )
            #创建商店集合
            self.db.stores.create_index(
            [("store_id", 1), ("books.book_id", 1)], unique=True
        )
            #创建新订单集合
            self.db.new_orders.create_index([("order_id", 1)], unique=True)
            #创建新订单详细信息集合
            self.db.new_order_details.create_index(
            [("order_id", 1), ("book_id", 1)], unique=True
        )
        except PyMongoError as e:
            logging.error(f"MongoDB initialization error: {e}")

    def get_db_conn(self):
        return self.db #返回数据库连接


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(uri="mongodb://localhost:27017/", db_name="bookstore"):
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
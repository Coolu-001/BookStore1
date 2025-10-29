import logging
import os
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
            for name in collections:
                if name not in self.db.list_collection_names():
                    self.db.create_collection(name)
                    logging.info(f"已创建集合: {name}")

                # 添加索引（防止重复）
            self.db["user"].create_index("user_id", unique=True)
            self.db["user_store"].create_index(
                [("user_id", 1), ("store_id", 1)], unique=True
            )
            self.db["store"].create_index(
                [("store_id", 1), ("book_id", 1)], unique=True
            )
            self.db["new_order"].create_index("order_id", unique=True)
            self.db["new_order_detail"].create_index(
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
    """
    初始化全局数据库连接实例。
    """
    global database_instance
    database_instance = Store(uri=uri, db_name=db_name)
    init_completed_event.set()


def get_db_conn():
    """
    获取全局数据库连接（数据库对象）
    """
    global database_instance
    if not database_instance:
        raise RuntimeError("数据库未初始化，请先调用 init_database()。")
    return database_instance.get_db_conn()
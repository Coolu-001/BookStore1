import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import threading


class Store:
    database: str

    def __init__(self,uri="mongodb://localhost:27017/", db_name="bookstore"):
        """
        uri: MongoDB 连接地址
        db_name: 数据库名称
        """
        try:
            # 保存参数并初始化 MongoClient
            self.uri = uri
            self.db_name = db_name
            # 创建一个长期存在的 MongoClient 实例并打开数据库
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]

            # 初始化集合和索引
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
            # 使用已经创建的 db 实例，get_db_conn() 会返回 self.db
            db = self.get_db_conn()

            # 创建用户集合
            db.user.create_index([("user_id", 1)], unique=True)
            
            # 创建用户-商店集合
            db.user_store.create_index(
                [("user_id", 1), ("store_id", 1)], unique=True
            )
            
            # 创建商店集合(嵌套文档结构)
            db.store.create_index(
                [("store_id", 1), ("books.book_id", 1)], unique=True 
            )
            
            # 创建新订单集合
            db.new_order.create_index([("order_id", 1)], unique=True)
            
            # 创建新订单详细信息集合
            db.new_order_detail.create_index(
                [("order_id", 1), ("book_id", 1)], unique=True
            )
            
            logging.info("数据库集合和索引初始化完成")
        
        except PyMongoError as e:
            logging.error(f"MongoDB initialization error: {e}")

    def get_db_conn(self):
        # 返回在 __init__ 中创建的同一个 db 实例
        return getattr(self, "db", None)



database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(uri="mongodb://localhost:27017/", db_name="bookstore"):
    global database_instance
    database_instance = Store(uri=uri, db_name=db_name)


def get_db_conn():
    global database_instance
    if database_instance is None:
        print("⚠️ 数据库未初始化，正在自动连接……")
        init_database()
        print ("连接好了")
    return database_instance.get_db_conn()
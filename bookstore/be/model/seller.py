from be.model import error
from .db_conn import DBConn
from pymongo.errors import PyMongoError


class Seller(DBConn):
    def __init__(self):
        super().__init__()
    
    # 上架书本
    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            # 使用嵌套文档结构
            self.db["store"].update_one(
                {"store_id": store_id},
                {
                    "$push": {
                        "books": {
                            "book_id": book_id,
                            "book_info": book_json_str,
                            "stock_level": stock_level
                        }
                    }
                },
                upsert=True  # 如果商店不存在则创建
            )
        except PyMongoError as e:
            return 528, str(e)
        except BaseException as e:
            return 530, str(e)
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            result = self.db["store"].update_one(
                {"store_id": store_id, "book_id": book_id},
                {"$inc": {"stock_level": add_stock_level}},
            )
            if result.matched_count == 0:
                return error.error_non_exist_book_id(book_id)
        except PyMongoError as e:
            return 528, str(e)
        except BaseException as e:
            return 530, str(e)
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> tuple[int, str]:
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            self.db["user_store"].insert_one({"store_id": store_id, "user_id": user_id})
        except PyMongoError as e:
            return 528, str(e)
        except BaseException as e:
            return 530, str(e)
        return 200, "ok"
    
###############分割线（待完善功能）###################
    def get_books(self, store_id: str):
        """获取商店的所有书籍"""
        try:
            store = self.db.store.find_one({"store_id": store_id})
            if not store:
                return error.error_non_exist_store_id(store_id)
            return 200, store.get("books", [])
        except PyMongoError as e:
            return 528, str(e)

    def remove_book(self, user_id: str, store_id: str, book_id: str):
        """下架书籍"""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            result = self.db.store.update_one(
                {"store_id": store_id},
                {"$pull": {"books": {"book_id": book_id}}}
            )
            if result.modified_count == 0:
                return error.error_non_exist_book_id(book_id)
            return 200, "ok"
        except PyMongoError as e:
            return 528, str(e)
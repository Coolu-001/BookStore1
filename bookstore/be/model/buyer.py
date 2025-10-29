from be.model import db_conn, error
from pymongo.errors import PyMongoError
import uuid
import json
from typing import List, Tuple


class Buyer(db_conn.DBConn):
    def __init__(self):
        super().__init__()  # 初始化 MongoDB 数据库连接

    def new_order(self, user_id: str, store_id: str, id_and_count: List[Tuple[str, int]]):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            # 生成唯一订单 ID
            uid = f"{user_id}_{store_id}_{uuid.uuid1()}"
            order_items = []
            total_price = 0

            for book_id, count in id_and_count:
                book = self.db["store"].find_one({"store_id": store_id, "book_id": book_id})
                if not book:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book.get("stock_level", 0)
                # book_info 可能是字符串（序列化的 JSON）或已经是 dict
                raw_book_info = book.get("book_info", {})
                if isinstance(raw_book_info, str):
                    try:
                        book_info_json = json.loads(raw_book_info)
                    except (ValueError, TypeError):
                        # 解析失败则回退到空 dict
                        book_info_json = {}
                elif isinstance(raw_book_info, dict):
                    book_info_json = raw_book_info
                else:
                    book_info_json = {}

                price = book_info_json.get("price", 0)

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 更新库存
                result = self.db["store"].update_one(
                    {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}},
                    {"$inc": {"stock_level": -count}},
                )
                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                order_items.append({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })
                total_price += price * count

            # 写入订单主表和详情表
            self.db["new_order"].insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "total_price": total_price
            })
            self.db["new_order_detail"].insert_many(order_items)
            order_id = uid

        except PyMongoError as e:
            return 528, str(e), ""
        except BaseException as e:
            return 530, str(e), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str):
        try:
            order = self.db["new_order"].find_one({"order_id": order_id})
            if not order:
                return error.error_invalid_order_id(order_id)

            buyer_id = order["user_id"]
            store_id = order["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            buyer = self.db["user"].find_one({"user_id": buyer_id})
            if not buyer:
                return error.error_non_exist_user_id(buyer_id)
            if buyer["password"] != password:
                return error.error_authorization_fail()

            store = self.db["user_store"].find_one({"store_id": store_id})
            if not store:
                return error.error_non_exist_store_id(store_id)

            seller_id = store["user_id"]
            seller = self.db["user"].find_one({"user_id": seller_id})
            if not seller:
                return error.error_non_exist_user_id(seller_id)

            total_price = order.get("total_price", 0)
            if buyer["balance"] < total_price:
                return error.error_not_sufficient_funds(order_id)

            # 更新余额
            self.db["user"].update_one({"user_id": buyer_id}, {"$inc": {"balance": -total_price}})
            self.db["user"].update_one({"user_id": seller_id}, {"$inc": {"balance": total_price}})

            # 删除订单记录
            self.db["new_order"].delete_one({"order_id": order_id})
            self.db["new_order_detail"].delete_many({"order_id": order_id})

        except PyMongoError as e:
            return 528, str(e)
        except BaseException as e:
            return 530, str(e)

        return 200, "ok"

    def add_funds(self, user_id, password, add_value):
        try:
            user = self.db["user"].find_one({"user_id": user_id})
            if not user:
                return error.error_authorization_fail()
            if user["password"] != password:
                return error.error_authorization_fail()

            self.db["user"].update_one({"user_id": user_id}, {"$inc": {"balance": add_value}})

        except PyMongoError as e:
            return 528, str(e)
        except BaseException as e:
            return 530, str(e)

        return 200, "ok"

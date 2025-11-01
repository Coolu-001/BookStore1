from be.model import db_conn, error
from pymongo.errors import PyMongoError
import uuid
import json
from typing import List, Tuple


class Buyer(db_conn.DBConn):
    def __init__(self):
        super().__init__()  

    def new_order(self, user_id: str, store_id: str, id_and_count: List[Tuple[str, int]]):
        order_id = ""
        try:
            if not id_and_count or any(count <= 0 for _, count in id_and_count):
                return error.error_invalid_params("Invalid book list") + (order_id,)
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            # 生成唯一订单 ID
            uid = f"{user_id}_{store_id}_{uuid.uuid1()}"
            order_items = []
            total_price = 0

            for book_id, count in id_and_count:
                store = self.db["store"].find_one({"store_id": store_id})
                if not store or "books" not in store:
                    return error.error_non_exist_store_id(store_id) + (order_id,)

            # 查找对应书籍
            book_item = next((b for b in store["books"] if b["book_id"] == book_id), None)
            if not book_item:
                print("❗DEBUG book_id:", book_id, error.error_non_exist_book_id(book_id))
                return error.error_non_exist_book_id(book_id) + (order_id,)

            stock_level = book_item.get("stock_level", 0)
            raw_book_info = book_item.get("book_info", {})
            if isinstance(raw_book_info, str):
                try:
                    book_info_json = json.loads(raw_book_info)
                except (ValueError, TypeError):
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
                {"store_id": store_id, "books.book_id": book_id, "books.stock_level": {"$gte": count}},
                {"$inc": {"books.$.stock_level": -count}},
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
            
            # 保存订单
            order_doc = {
                "order_id": uid,
                "user_id": user_id,
                "store_id": store_id,
                "books": order_items,
                "total_price": total_price,
                "status": "unpaid"
            }
            self.db["new_order"].insert_one(order_doc)

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
########待添加#####
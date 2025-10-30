import jwt
import time
import logging
from pymongo.errors import PyMongoError, DuplicateKeyError
from be.model import error
from be.model.db_conn import DBConn  # MongoDB 连接类


def jwt_encode(user_id: str, terminal: str) -> str:
    return jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )


def jwt_decode(encoded_token, user_id: str) -> str:
    return jwt.decode(encoded_token, key=user_id, algorithms=["HS256"])


class User(DBConn):
    token_lifetime: int = 3600  # 有效期一小时

    def __init__(self):
        super().__init__()
        self.user_col = self.db["user"]  # MongoDB 中的 user 集合

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False
        
    # 注册
    def register(self, user_id: str, password: str):
        terminal = f"terminal_{time.time()}"
        token = jwt_encode(user_id, terminal)
        try:
            self.user_col.insert_one({
                "_id": user_id,  # 用 user_id 做唯一键
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal
            })
        except DuplicateKeyError:
            return error.error_exist_user_id(user_id)
        except PyMongoError as e:
            return 528, f"Database error: {str(e)}", ""
        return 200, "ok"
    
    # 检查权限
    def check_token(self, user_id: str, token: str):
        try:
            user = self.user_col.find_one({"_id": user_id})
            if not user:
                return error.error_authorization_fail()
            db_token = user.get("token")
            if not self.__check_token(user_id, db_token, token):
                return error.error_authorization_fail()
            return 200, "ok"
        except PyMongoError as e:
            return 528, f"Database error: {str(e)}", ""
    
    # 检查密码
    def check_password(self, user_id: str, password: str):
        try:
            user = self.user_col.find_one({"_id": user_id})
            if not user or user.get("password") != password:
                return error.error_authorization_fail()
            return 200, "ok"
        except PyMongoError as e:
            return 528, f"Database error: {str(e)}", ""

    # 登陆
    def login(self, user_id: str, password: str, terminal: str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            result = self.user_col.update_one(
                {"_id": user_id},
                {"$set": {"token": token, "terminal": terminal}}
            )
            if result.matched_count == 0:
                return error.error_authorization_fail() + ("",)
            return 200, "ok", token
        except PyMongoError as e:
            return 528, f"Database error: {str(e)}", ""

    #登出
    def logout(self, user_id: str, token: str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = f"terminal_{time.time()}"
            dummy_token = jwt_encode(user_id, terminal)

            result = self.user_col.update_one(
                {"_id": user_id},
                {"$set": {"token": dummy_token, "terminal": terminal}}
            )
            if result.matched_count == 0:
                return error.error_authorization_fail()
            return 200, "ok"
        except PyMongoError as e:
            return 528, f"Database error: {str(e)}", ""

    # 注销账户
    def unregister(self, user_id: str, password: str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            result = self.user_col.delete_one({"_id": user_id})
            if result.deleted_count == 0:
                return error.error_authorization_fail()
            return 200, "ok"
        except PyMongoError as e:
            return 528, f"Database error: {str(e)}", ""

    # 修改密码
    def change_password(self, user_id: str, old_password: str, new_password: str):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = f"terminal_{time.time()}"
            token = jwt_encode(user_id, terminal)
            result = self.user_col.update_one(
                {"_id": user_id},
                {"$set": {
                    "password": new_password,
                    "token": token,
                    "terminal": terminal
                }}
            )
            if result.matched_count == 0:
                return error.error_authorization_fail()
            return 200, "ok"
        except PyMongoError as e:
            return 528, f"Database error: {str(e)}", ""

###############待添加新功能
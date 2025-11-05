import requests
from urllib.parse import urljoin


class Auth:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "auth/") 

    # 用户登录
    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        payload = {"user_id": user_id, "password": password, "terminal": terminal}
        endpoint = urljoin(self.url_prefix, "login")
        response = requests.post(endpoint, json=payload)
        return response.status_code, response.json().get("token")

    # 用户注册
    def register(self, user_id: str, password: str) -> int:
        payload = {"user_id": user_id, "password": password}
        endpoint = urljoin(self.url_prefix, "register")
        response = requests.post(endpoint, json=payload)
        return response.status_code

    # 修改密码
    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        payload = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        endpoint = urljoin(self.url_prefix, "password")
        response = requests.post(endpoint, json=payload)
        return response.status_code

    # 用户登出
    def logout(self, user_id: str, token: str) -> int:
        payload = {"user_id": user_id}
        headers = {"token": token} 
        endpoint = urljoin(self.url_prefix, "logout")
        response = requests.post(endpoint, headers=headers, json=payload)
        return response.status_code

    # 用户注销
    def unregister(self, user_id: str, password: str) -> int:
        payload = {"user_id": user_id, "password": password}
        endpoint = urljoin(self.url_prefix, "unregister")
        response = requests.post(endpoint, json=payload)
        return response.status_code

    # 搜索图书
    def search_book(self, title='', content='', tag='', store_id='') -> int:
        payload = {"title": title, "content": content, "tag": tag, "store_id": store_id}
        endpoint = urljoin(self.url_prefix, "search_book")
        response = requests.post(endpoint, json=payload)
        # 如果没有找到匹配的图书，可以根据需要返回自定义的消息
        # if r.status_code == 529:
        #     return r.status_code, "No matching books found."
        return response.status_code  

import os
import random
import base64
import pymongo

# 存储图书的相关信息
class Book:
    def __init__(self):
        self.tags = []
        self.pictures = []

    # 图书的基本属性
    id: str  # 图书ID
    title: str  # 图书标题
    author: str  # 作者
    publisher: str  # 出版社
    original_title: str  # 原书名
    translator: str  # 译者
    pub_year: str  # 出版年份
    pages: int  # 页数
    price: int  # 价格
    binding: str  # 装帧类型
    isbn: str  # ISBN号
    author_intro: str  # 作者简介
    book_intro: str  # 图书简介
    content: str  # 内容简介
    tags: [str]  # 标签列表
    pictures: [bytes]  # 图书图片列表


# 与数据库的交互
class BookDB:
    __socket = None
    __db = None

    def __init__(self, not_used_param: bool = False):
        # 初始化数据库连接
        #注释行专为本地数据库使用 
        # 使用环境变量中的 MONGODB_API 连接到 MongoDB 数据库
        self.socket = pymongo.MongoClient(os.getenv('MONGODB_API'), server_api=pymongo.server_api.ServerApi('1'))
        # self.socket = pymongo.MongoClient('mongodb://localhost:27017')  # 也可以直接连接到本地数据库
        self.db = self.socket['bookstore']  # 选择 'bookstore' 数据库

        # 为 'books' 集合的 'id' 字段创建索引，提高查询效率
        try:
            self.db['books'].create_index([("id", pymongo.ASCENDING)])
        except:
            pass
        
    # 获取数据库中图书的总数
    def get_book_count(self):
        return self.db['books'].count_documents({}) 

    # 获取指定范围内的图书信息
    def get_book_info(self, start, size) -> [Book]:
        books = []  # 用于存储图书对象的列表
        # 查询 'books' 集合中的数据，跳过前 'start' 条记录，限制返回 'size' 条记录
        cursor = self.db['books'].find().skip(start).limit(size)
        for doc in cursor:
            book = Book()
            book.id = doc.get("id") 
            book.title = doc.get("title") 
            book.author = doc.get("author") 
            book.publisher = doc.get("publisher") 
            book.original_title = doc.get("original_title") 
            book.translator = doc.get("translator") 
            book.pub_year = doc.get("pub_year")  
            book.pages = doc.get("pages")  
            book.price = doc.get("price")  
            book.currency_unit = doc.get("currency_unit")  
            book.binding = doc.get("binding") 
            book.isbn = doc.get("isbn") 
            book.author_intro = doc.get("author_intro")
            book.book_intro = doc.get("book_intro")  
            book.content = doc.get("content") 
            tags = doc.get("tags")  
            picture = doc.get("picture")

            # 处理标签
            for tag in tags.split("\n"):  
                if tag.strip() != "": 
                    book.tags.append(tag) 

            # 处理图书图片，将其编码为 base64 字符串并添加到图片列表
            for i in range(0, random.randint(0, 9)):  
                if picture is not None:  
                    encode_str = base64.b64encode(picture).decode("utf-8")  
                    book.pictures.append(encode_str) 
            
            books.append(book)  
        return books
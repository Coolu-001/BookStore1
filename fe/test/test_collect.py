import pytest

from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid
from fe.test.gen_book_data import GenBook


class TestCollection:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_new_collection_user_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_collection_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_collection_buyer_id_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_new_collection_seller_id_{}".format(str(uuid.uuid1()))
        
        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, 2)

        yield

    def test_ok(self):
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_id)
        self.seller = register_new_seller(self.seller_id, self.seller_id)
        
        # 测试收藏书籍
        for b in self.books:
            code = self.buyer.add_favorite_book(b.id)
            assert code == 200
        
        # 测试获取收藏书籍
        code = self.buyer.get_books_favorite(self.buyer_id)
        assert code == 200
        
        # 测试取消收藏书籍
        for b in self.books:
            code = self.buyer.remove_favorite_book(b.id)
            assert code == 200

        # 测试收藏店铺
        self.seller.create_store(self.store_id)
        code = self.buyer.add_favorite_store(self.store_id)
        assert code == 200
        
        # 测试获取收藏店铺
        code = self.buyer.get_stores_favorite(self.buyer_id)
        assert code == 200
        
        # 测试取消收藏店铺
        code = self.buyer.remove_favorite_store(self.store_id)
        assert code == 200
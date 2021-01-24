# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from copy import deepcopy

from itemadapter import ItemAdapter
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors

class JdbookPipeline:
    # 同步存储
    def __init__(self):
        db_params = {
            "host":"127.0.0.1",
            "port":3306,
            "user":"root",
            "password":"123456",
            "database":"jd",
            "charset":"utf8"
        }
        self.conn = pymysql.connect(**db_params)
        self.cursor = self.conn.cursor()
        self._sql = None

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
                insert into book(big_cate,small_href,small_cate,page,book_url,book_img,book_price,book_name,book_publish_house) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            return self._sql
        return self._sql

    def process_item(self, item, spider):
        self.cursor.execute(self.sql,(item["big_cate"],item["small_href"],item["small_cate"],item["page"],item["book_url"],item["book_img"],item["book_price"],item["book_name"],item["book_publish_house"]))
        self.conn.commit()
        return item

class JdbookAsyncPipeline(object):
    def __init__(self):
        db_params = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "123456",
            "database": "jd",
            "charset": "utf8",
            "cursorclass": cursors.DictCursor  # 游标类型
        }
        self.dbpool = adbapi.ConnectionPool("pymysql", **db_params)
        # 告诉twisted使用的是什么存储模块

        self._sql = None

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
                 insert into book(big_cate,small_href,small_cate,page,book_url,book_img,book_price,book_name,book_publish_house) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
             """
            return self._sql
        return self._sql

    def insert_item(self, cursor, item):
        # 插入数据函数
        cursor.execute(self.sql, (
        item["big_cate"], item["small_href"], item["small_cate"], item["page"], item["book_url"], item["book_img"],
        item["book_price"], item["book_name"], item["book_publish_house"]))

    def handle_error(self, error, item, spider):
        # 错误处理函数
        print("=" * 20)
        print(error)
        print("=" * 20)

    def process_item(self, item, spider):
        deep_item = deepcopy(item)
        defer = self.dbpool.runInteraction(self.insert_item, deep_item)
        # 编写函数通过runInteraction存储数据库，如果不使用这个方法和同步没有区别
        defer.addErrback(self.handle_error, item, spider)
        # 处理错误信息
        return item

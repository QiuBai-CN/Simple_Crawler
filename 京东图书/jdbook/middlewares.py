# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time
from scrapy import signals
from fake_useragent import UserAgent
from scrapy.http.response.html import HtmlResponse
from selenium import webdriver
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class JdbookUserAgentMiddleware:
    def __init__(self):
        self.ua = UserAgent()

    def process_request(self, request, spider):
        request.headers["User-Agent"] = self.ua.random

class JdbookSeleniumMiddleware:
    """
    首页有反爬机制，所以使用selenium构建好html源码之后在作为response返回
    """
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path="E:\chromedriver\chromedriver.exe")

    def process_request(self, request, spider):
        if request.url == "https://book.jd.com/booksort.html":
            self.driver.get(request.url)
            self.driver.implicitly_wait(1)
            source = self.driver.page_source
            response = HtmlResponse(url=self.driver.current_url,body=source,request=request,encoding="utf-8")
            self.driver.quit()
            return response





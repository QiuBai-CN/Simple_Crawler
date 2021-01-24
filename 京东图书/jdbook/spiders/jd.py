import re
import scrapy
from copy import deepcopy
import scrapy_redis.spiders
from jdbook.items import JdbookItem

class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = ['https://book.jd.com/booksort.html']
    #redis_key = "jd:start_url"

    def parse(self, response):
        dts = response.xpath("//div[@class='mc']//dt")  # 大分类列表
        item = JdbookItem()
        for dt in dts:
            item["big_cate"] = dt.xpath("./a/text()").get()  # 获取大分类名字
            ems = dt.xpath("./following-sibling::dd[1]/em")  # 小分类列表
            for em in ems:
                item["small_href"] = em.xpath("./a/@href").get()
                item["small_cate"] = em.xpath("./a/text()").get()
                item["page"] = 1
                if item["small_href"] is not None:
                    """
                    https://list.jd.com/list.html?cat=1713%2C3258%2C3297&page=1
                    从点击上述类型网站，往下拉会发现是通过Ajax进行加载，点击下一页之后发现URL的page
                    是以奇数递增的方式，但是手动输入偶数页面也是可以访问，并且访问的内容就是前面奇数
                    页面的Ajax的数据
                    """
                    item["small_href"] = item["small_href"].replace("-", "%2C")
                    item["small_href"] = item["small_href"].replace(".html", "&page=")
                    temp = item["small_href"].split("/")
                    item["small_href"] = "https://" + temp[2] + "/list.html?cat=" + temp[3] + str(item["page"])
                    yield scrapy.Request(url=item["small_href"], callback=self.parse_book_list,
                                         meta={"item": item})

    def parse_book_list(self, response):
        item = response.meta["item"]
        lis = response.xpath("//div[@id='J_goodsList']//li")
        for li in lis:
            item["book_url"] = "https:" + li.xpath(".//div[@class='p-img']/a/@href").get()
            if "https:" not in item["book_url"]:
                item["book_url"] = "https:" + item["book_url"]
            item["book_img"] = li.xpath(".//div[@class='p-img']/a/img/@src").get()
            if item["book_img"] is None:
                item["book_img"] = li.xpath(".//div[@class='p-img']/a/img/@data-lazy-img").get()
            item["book_img"] = "https:" + item["book_img"]
            item["book_price"] = "".join(li.xpath(".//div[@class='p-price']//text()").getall()).strip()
            item["book_name"] = li.xpath(".//div[@class='p-name']/a/em/text()").get().strip()
            item["book_publish_house"] = li.xpath(".//span[@class='p-bi-store']/a/text()").get()
            yield item

        item["page"] = item["page"] + 1 #通过URL的规律不需要进行Ajax的破解只需要每一页加1就可以获取到所有的数据
        next_url = re.findall(r"(https://list.jd.com/list.html\?cat=.+&page=)\d+", item["small_href"])[0]
        #通过正则表达式从small_href中取出https://list.jd.com/list.html\?cat=.+&page=
        next_url = next_url + str(item["page"])
        yield scrapy.Request(url=next_url, callback=self.parse_book_list, meta={"item": item})












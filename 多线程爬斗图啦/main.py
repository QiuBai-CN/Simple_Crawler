import requests
from lxml import etree
from urllib import request
import os
from queue import Queue
import re
import threading
"""
    利用生产者消费者模式多线程下载表情包
    1、先获取每一页的URL
    2、利用生产者获取每一张图片的URL
    3、将图片URL放入全局的一个URL存储池中
    4、利用消费者去下载每一张图片
"""
class Producer(threading.Thread):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Producer,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_url(url)

    def parse_url(self,url):
        resp = requests.get(url=url, headers=self.header)
        text = resp.text
        html = etree.HTML(text)
        imgs = html.xpath("//div[@class='page-content text-center']//img[@class!='gif']")
        for img in imgs:
            img_url = img.get("data-original")
            # get方法可以直接获取img标签中的一些属性
            img_name = img.get("alt")
            img_name = re.sub(r'[\?？\.，。!！\*\\\<]', '', img_name)
            # 获取文件名
            img_suffix = os.path.splitext(img_url)[1]
            # 获取文件后缀，通过os.path.splitext函数,以元组的方式返回
            filename = img_name + img_suffix
            self.img_queue.put((img_url,filename))

class Consumer(threading.Thread):
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Consumer,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break
            img_url,filename = self.img_queue.get()
            request.urlretrieve(img_url, "images/{}".format(filename))
            print(filename + " " + "下载完成！")


def main():
    page_queue = Queue(100)
    #因为要下载100页的表情包，所以页面的URL生成100页
    img_queue = Queue(500)
    for x in range(1,101):
        url = "https://www.doutula.com/photo/list/?page=%d" % x
        page_queue.put(url)
        #把页面URL传递到队列中

    for x in range(5):
        t = Producer(page_queue,img_queue)
        t.start()

    for x in range(5):
        t = Consumer(page_queue,img_queue)
        t.start()

if __name__ == '__main__':
    main()

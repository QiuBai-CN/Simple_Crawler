import os
import re
import threading
from queue import Queue
from urllib import request

import requests
from lxml import etree


class Producer(threading.Thread):
    def __init__(self,page_queue,img_queue):
        super(Producer,self).__init__()
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_url(url)

    def parse_url(self,url):
        resp = requests.get(url)
        text = resp.text
        html = etree.HTML(text)
        imgs = html.xpath("//div[@class='page-content text-center']//img")
        for img in imgs:
            img_url = img.get("data-original")
            img_name = img.get("alt")
            img_name = re.sub(r"[\\？ \* \| “ \< \> \: /]","",img_name)
            img_suffix = os.path.splitext(img_url)[1]
            filename = img_name + img_suffix
            self.img_queue.put((filename,img_url))


class Comsumer(threading.Thread):
    def __init__(self,page_queue,img_queue):
        super(Comsumer,self).__init__()
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty() and self.img_queue.empty():
                break
            filename,img_url = self.img_queue.get()
            request.urlretrieve(img_url,"images/{}".format(filename))
            print(filename + " 下载完成！！")


def main():
    page_queue = Queue(10)
    img_queue = Queue(100)

    for x in range(1,11):
        url = "https://www.doutula.com/photo/list/?page={}".format(x)
        page_queue.put(url)
    
    for x in range(10):
        t = Producer(page_queue,img_queue)
        t.start()

    for x in range(100):
        t = Comsumer(page_queue,img_queue)
        t.start()

if __name__ == '__main__':
    main()
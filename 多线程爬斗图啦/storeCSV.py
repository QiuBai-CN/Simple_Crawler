import threading
from queue import Queue
import requests
from lxml import etree
import re
import os
import csv
class Producer(threading.Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    def __init__(self, page_queue, url_queue):
        super(Producer,self).__init__()
        self.page_queue = page_queue
        self.url_queue = url_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_url(url)

    def parse_url(self,url):
        resp = requests.get(url,headers=self.headers)
        text = resp.text
        html = etree.HTML(text)
        imgs = html.xpath("//div[@class='page-content text-center']//img[@class!='gif']")
        for img in imgs:
            img_url = img.get("data-original")
            img_name = img.get("alt")
            img_name = re.sub(r'[? “ ”/ \\ < > \* \| : ]',"",img_name)
            img_suffix = os.path.splitext(img_url)[1]
            filename = img_name + img_suffix
            print(filename)
            self.url_queue.put((img_url,filename))


class Consumer(threading.Thread):
    def __init__(self, page_queue, url_queue,writer, gLock):
        super(Consumer, self).__init__()
        self.page_queue = page_queue
        self.writer = writer
        self.gLock = gLock
        self.url_queue = url_queue

    def run(self):
        while True:
            if self.url_queue.empty() and self.page_queue.empty():
                break
            url = self.url_queue.get()
            img_url, filename = url
            self.gLock.acquire()
            self.writer.writerow([img_url,filename])
            self.gLock.release()
            print("保存一条")


def main():
    page_queue = Queue(10)
    url_queue = Queue(100)
    fp = open("imgurl.csv","a",encoding="utf-8",newline="")
    writer = csv.writer(fp)
    gLock = threading.Lock()


    for x in range(10):
        url = "https://www.doutula.com/photo/list/?page=%d" % x
        page_queue.put(url)

    for x in range(5):
        t = Producer(page_queue,url_queue)
        t.start()

    for x in range(5):
        t = Consumer(page_queue,url_queue,writer,gLock)
        t.start()

    #fp.close()


if __name__ == '__main__':
    main()
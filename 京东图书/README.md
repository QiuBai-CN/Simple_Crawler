# JDBook
这是一个爬取京东所有类别的图书的信息的爬虫
## V1.0
初步完成了全类别的爬取，start_urls通过了selenium获得page_source，不然会被反爬，无法整理每个分类的URL  
遗留问题：  
1、商品页面有60个商品一半正常能爬取，一半通过ajax获取，后期把反爬到位  
2、会添加Scrapy-redis和Mysql作为存储
## V1.1
已添加Mysql的同步和异步存储
## V1.2
已添加Scrapy-redis  
如果不想使用Scrapy-redis，请做如下修改： 
  
jd.py中：  
修改爬虫继承的父类从scrapy_redis.spiders.RedisSpider改回为scrapy.Spider；  
redis_key删除，删除start_urls的注释  
  
settings.py中：  
删除SCHEDULER_PERSIST,REDIS_HOST,REDIS_PORT,REDIS_PARAMS  
修改ITEM_PIPELINES,删除scrapy_redis的pipelines,恢复之前的pipelines  
  
## 遗留问题解决  
关于Ajax，可以分析页面的URL地址，通过修改URL中的Page参数可以直接绕过Ajax  

## V1.3  
在Mysql的异步存储的时候会出现重复数据的情况，原因是self.dbpool.runInteraction是一个异步操作，item在共享的时候出现了问题，解决方法就是在存储的时候深拷贝一份item，这样可能会影响性能


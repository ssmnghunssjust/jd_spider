# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     push_cate.py 
   Description :   把mongodb的category信息写入到redis
        1、 连接mongodb
        2、 连接redis
        3、 读取mongodbcategory信息，序列化后，添加到redis_key中指定的list
        4、 关闭mongodb
   Author :        LSQ
   date：          2020/7/29
-------------------------------------------------
   Change Activity:
                   2020/7/29: None
-------------------------------------------------
"""
import pickle
from pymongo import MongoClient
from redis import StrictRedis
from jd_spider.settings import MONGODB_URI, REDIS_URL
from jd_spider.spiders.jd_product import JdProductSpider

def push_to_redis():
    mongo = MongoClient(MONGODB_URI)
    redis = StrictRedis.from_url(REDIS_URL)
    collection = mongo['jd_spider']['category']
    # cate_cursor = collection.find({'inner_cate_url':{'$not':{'$regex':'.*channel'}}})

    # for cate in cate_cursor:
    #     data = pickle.dumps(cate)
    #     redis.lpush(JdProductSpider.redis_key, data)
    category = collection.find_one({'inner_cate_url':{'$not':{'$regex':'.*channel'}}})
    data = pickle.dumps(category)
    redis.lpush(JdProductSpider.redis_key, data)
    mongo.close()

if __name__ == '__main__':
    push_to_redis()
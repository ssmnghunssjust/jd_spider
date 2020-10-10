# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import pickle
from itemadapter import ItemAdapter
from pymongo import MongoClient
from jd_spider.spiders.jd_category import JdCategorySpider
from jd_spider.spiders.jd_product import JdProductSpider
from .settings import MONGODB_URI
from scrapy.exceptions import DropItem
from redis.client import StrictRedis


class JdCategoryPipeline:

    def open_spider(self, spider):
        if isinstance(spider, JdCategorySpider):
            self.client = MongoClient(spider.settings.get('MONGODB_URI'))   # 也可以直接用从settings文件导入的MONGODB_URI
            self.collection = self.client['jd_spider']['category']
            self.redis = StrictRedis.from_url(spider.settings.get('REDIS_URL'))

            # 只插入一个item，用做测试
            item = {
                "outer_cate_title": "家用电器",
                "outer_cate_url": "https://jiadian.jd.com",
                "middle_cate_title": "电视",
                "middle_cate_url": "https://list.jd.com/list.html?cat=737,794,798",
                "inner_cate_title": "超薄电视",
                "inner_cate_url": "https://list.jd.com/list.html?cat=737,794,798&ev=4155_76344&sort=sort_rank_asc&trans=1&JL=2_1_0#J_crumbsBar"
            }
            data = pickle.dumps(item)
            self.redis.rpush(JdProductSpider.redis_key, data)

    def close_spider(self, spider):
        if isinstance(spider, JdCategorySpider):
            self.client.close()

    def process_item(self, item, spider):
        '''
        必须返回字典或item对象，或者抛出DropItem异常
        from scrapy.exceptions import DropItem
        :param item:
        :param spider:
        :return:
        '''
        if isinstance(spider, JdCategorySpider):

                self.collection.insert_one(dict(item))
                # 排除非列表页的内部分类
                # if item['inner_cate_url'].find('list.') != -1:
                #     data = pickle.dumps(item)
                #     self.redis.rpush(JdProductSpider.redis_key, data)
        return item

class JdProductPipeline:

    def open_spider(self, spider):
        if isinstance(spider, JdProductSpider):
            self.client = MongoClient(spider.settings.get('MONGODB_URI'))   # 也可以直接用从settings文件导入的MONGODB_URI
            self.collection = self.client['jd_spider']['product']

    def close_spider(self, spider):
        if isinstance(spider, JdProductSpider):
            self.client.close()

    def process_item(self, item, spider):
        if isinstance(spider, JdProductSpider):
            count = self.collection.count_documents({'product_sku_id': item['product_sku_id']})
            if count == 0:
                self.collection.insert_one(dict(item))
            else:
                spider.logger.warn(f'商品 {item["product_sku_id"]}已存在!')
                print(f'商品 {item["product_sku_id"]}已存在!')
        return item

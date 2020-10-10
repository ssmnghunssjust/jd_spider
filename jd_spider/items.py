# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JdSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

'''
分类数据模型：分类信息category（cate）
    outter_cate_title: 大分类名称
    outer_cate_url: 大分类url
    middle_cate_title: 中分类名称
    middle_cate_url: 中分类url
    inner_cate_title: 小分类名称
    inner_cate_url: 小分类url
'''

class Category(scrapy.Item):
    outer_cate_title = scrapy.Field()
    outer_cate_url = scrapy.Field()
    middle_cate_title = scrapy.Field()
    middle_cate_url = scrapy.Field()
    inner_cate_title = scrapy.Field()
    inner_cate_url = scrapy.Field()

'''
商品数据模型：商品信息（product）
    product_category: 商品类别
    product_sku_id: 商品ID
    product_title: 商品名称
    product_img_url: 商品图片url
    product_book_info: 图书信息，作者，出版社
    product_option: 商品选项
    product_shop: 商品店铺
    product_comments: 商品评论数量
    product_ad: 商品促销
    product_price: 商品价格
'''

class Product(scrapy.Item):
    product_category = scrapy.Field()
    product_sku_id = scrapy.Field()
    product_title = scrapy.Field()
    product_img_url = scrapy.Field()
    product_book_info = scrapy.Field()
    product_option = scrapy.Field()
    product_shop = scrapy.Field()
    product_comments = scrapy.Field()
    product_ad = scrapy.Field()
    product_price = scrapy.Field()
    product_url = scrapy.Field()
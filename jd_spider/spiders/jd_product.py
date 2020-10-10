import scrapy
import re
import json
import pickle

from jd_spider.items import Product
from scrapy_redis.spiders import RedisSpider


class JdProductSpider(RedisSpider):
    name = 'jd_product'
    allowed_domains = ['jd.com', '3.cn']

    redis_key = 'jd_product:category'

    # start_urls = ['http://jd.com/']

    # def start_requests(self):
    #     category = {
    #         "outer_cate_title": "家用电器",
    #         "outer_cate_url": "https://jiadian.jd.com",
    #         "middle_cate_title": "电视",
    #         "middle_cate_url": "https://list.jd.com/list.html?cat=737,794,798",
    #         "inner_cate_title": "超薄电视",
    #         "inner_cate_url": "https://list.jd.com/list.html?cat=737,794,798&ev=4155_76344&sort=sort_rank_asc&trans=1&JL=2_1_0#J_crumbsBar"
    #     }
    #     return [scrapy.Request(
    #         category['inner_cate_url'],
    #         callback=self.parse,
    #         meta={'category': category}
    #     )]

    def make_request_from_data(self, data):
        '''
        根据redis中的二进制分类数据，构建请求
        :param data: 分类信息的二进制数据
        :return: 使用inner_cate_url构建请求对象
        '''
        category = pickle.loads(data)
        return scrapy.Request(
            category['inner_cate_url'],
            callback=self.parse,
            meta={'category': category, 'referer': category['inner_cate_url'], 'item_start': 1}
            # item_start用于控制翻页请求中的{s}
        )

    def parse(self, response):
        '''
        解析商品列表页
        :param response:
        :return:
        '''
        category = response.meta['category']

        # 解决商品详情页和商品列表页翻页的referer反爬问题
        referer = response.meta['referer']
        headers = {'referer': referer}

        item_start = response.meta['item_start']

        # 获取商品列表
        goods_li_list = response.xpath('//div[@id="J_goodsList"]/ul/li') if len(
            response.xpath('//div[@id="J_goodsList"]/ul/li')) > 0 else response.xpath('//div[@id="plist"]/ul/li')

        # 遍历商品列表，获取商品sku_id和商品详情页面url，并向该url发起请求
        for li in goods_li_list:
            product = Product()
            product['product_sku_id'] = li.xpath('./@data-sku').extract_first()
            product['product_url'] = 'https:' + li.xpath('.//div[contains(@class, "p-name")]/a/@href').extract_first()

            yield scrapy.Request(
                product['product_url'],
                callback=self.parse_detail,
                headers=headers,
                meta={'product': product, 'product_category': category},
                priority=1,
            )

        # 构造翻页请求
        # next_url_base = 'https://list.jd.com/listNew.php?{base_url}&page={page}&s=28&scrolling=y&log_id={log_id}&tpl=1_M&isList={isList}&show_items={show_items}'
        next_url_base_1 = 'https://list.jd.com/listNew.php?{base_url}&page={page}&s={s}&scrolling=y&log_id={log_id}&tpl=1_M&show_items={show_items}'
        next_url_base_2 = 'https://list.jd.com/listNew.php?{base_url}&page={page}&s={s}&click={click}'
        'https://coll.jd.com/list.html?sub=36582&page=3&JL=6_0_0'
        response_decode = response.body.decode()
        # print(response_decode)
        if len(re.findall("base_url=\"(.*?)\";", response_decode)) > 0:
            base_url = re.findall("base_url=\"(.*?)\";", response_decode)[0]
        elif len(re.findall('baseURL = "(.*?)";', response_decode)) > 0:
            base_url = re.findall('baseURL = "(.*?)";', response_decode)[0]
        else:
            base_url = re.findall("baseURL = '(.*?)';", response_decode)[0]
        if len(re.findall("page:'(.*?)'", response_decode)) > 0 :
            page = re.findall("page:'(.*?)'", response_decode)[0]
        else:
            page = re.findall('"page":(.*?),', response_decode)[0]
        item_start += 30
        if int(page) % 2 == 1:
            log_id = re.findall("log_id:'(.*?)',", response_decode)[0]
            show_items = re.findall("wids:'(.*?)',", response_decode)[0]
            next_url = next_url_base_1.format(base_url=base_url, page=str(int(page) + 1), s=str(item_start),
                                              log_id=log_id,
                                              show_items=show_items)
        else:
            next_url = next_url_base_2.format(base_url=base_url, page=str(int(page) + 1), s=str(item_start), click='0')
        page_count = re.findall("page_count:'(.*?)'", response_decode)[0]
        referer_base = 'https://list.jd.com/list.html?{base_url}&page={page}&s={s}&click={click}'
        if int(page) == 1:
            referer = category['inner_cate_url']
        else:
            if int(page) % 2 == 0:
                referer = referer_base.format(base_url=base_url, page=str(int(page) + 1), s=str(item_start), click='0')
        if page != page_count:
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                headers=headers,
                meta={'category': category, 'referer': referer, 'item_start': item_start}
            )

    def parse_detail(self, response):
        '''
        解析商品详情页，获取商品相关信息
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
        :param response:
        :return:
        '''
        print('正在解析sku_id：%s商品' % response.meta['product']['product_sku_id'])
        print('商品页的字符长度为：%s' % len(response.body.decode()))
        product = response.meta['product']
        product_category = response.meta['product_category']
        response_body = response.body.decode()
        # print(response_body)
        product['product_category'] = product_category
        product['product_title'] = re.findall("name:\s*'(.*?)',", response_body)[0]
        product['product_img_url'] = eval(re.findall("imageList:\s*(.*),", response_body)[0])
        product['product_img_url'] = ['https://img13.360buyimg.com/n1/' + img_url for img_url in
                                      product['product_img_url']]
        product['product_shop'] = response.xpath(
            '//div[@id="crumb-wrap"]//div[contains(@class, "contact")]//div[@class="name"]/a/text()').extract_first()
        product['product_option'] = eval(re.findall('colorSize:\s*(.*),\s*warestatus', response_body)[0])

        # 构造商品促销信息请求，获取商品促销、优惠券等相关信息
        v2_url_base = 'https://cd.jd.com/promotion/v2?skuId={skuId}&area={area}&cat={cat}'

        # cookie_str = response.request.headers.get('cookie').decode()
        # cookie_dict = {i.split('=')[0]: i.split('=')[1] for i in cookie_str.split(';')}
        # area = cookie_dict['ipLoc-djd'].replace('-', '_')
        area = '19-1601-3633-0'.replace('-', '_')
        cat = ','.join(re.findall('cat:\s*\[(.*?)\],', response_body)[0].split(','))
        v2_url = v2_url_base.format(skuId=product['product_sku_id'], area=area, cat=cat)
        yield scrapy.Request(
            v2_url,
            callback=self.parse_product_ad,
            meta={'product': product},
            priority=1,
        )

    def parse_product_ad(self, response):
        product = response.meta['product']
        print('正在解析%s的促销信息' % product['product_sku_id'])
        response_json = json.loads(response.body.decode())
        print(response_json)
        ad = response_json.get('ads')[0].get('ad')
        if '<a' in ad:
            product['product_ad'] = re.sub(r'<a.*a>$', '', ad, re.S)
        else:
            product['product_ad'] = ad

        # 构造商品价格请求，获取商品价格信息
        mgets_url_base = 'https://p.3.cn/prices/mgets?skuIds=J_{}'
        mgets_url = mgets_url_base.format(product['product_sku_id'])

        yield scrapy.Request(
            mgets_url,
            callback=self.parse_product_price,
            meta={'product': product},
            priority=1,
        )

    def parse_product_price(self, response):
        product = response.meta['product']
        print('正在解析%s的价格信息' % product['product_sku_id'])
        response_json = response.body.decode()
        product['product_price'] = eval(response_json)[0]['p']

        # 构造商品评价请求，获取商品评价信息
        # comments_url_base = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'
        # comments_url = comments_url_base.format(product['product_sku_id'])
        # comments_url_base = 'https://club.jd.com/comment/skuProductPageComments.action?productId={}&score=0&sortType=5&page=0'
        comments_url_base = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'
        comments_url = comments_url_base.format(product['product_sku_id'])

        yield scrapy.Request(
            comments_url,
            callback=self.parse_product_comments_summary,
            meta={'product': product},
            priority=1,
        )

    def parse_product_comments_summary(self, response):
        product = response.meta['product']
        print('正在解析%s的评价信息' % product['product_sku_id'])
        # product_comment_summary = json.loads(response.body.decode('GBK'))['productCommentSummary']
        CommentsCount = json.loads(response.body.decode('GBK'))['CommentsCount'][0]
        product['product_comments'] = {
            'comment_count': CommentsCount['CommentCount'],
            'default_good_count': CommentsCount['DefaultGoodCount'],
            'good_count': CommentsCount['GoodCount'],
            'good_rate': CommentsCount['GoodRate'],
            'general_count': CommentsCount['GeneralCount'],
            'general_rate': CommentsCount['GeneralRate'],
            'poor_count': CommentsCount['PoorCount'],
            'poor_rate': CommentsCount['PoorRate'],
        }
        print(product['product_comments'])
        print('商品%s保存成功' % product['product_sku_id'])
        yield product

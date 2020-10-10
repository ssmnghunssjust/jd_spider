import scrapy
import json

from jd_spider.items import Category


class JdCategorySpider(scrapy.Spider):
    name = 'jd_category'
    allowed_domains = ['3.cn']
    start_urls = ['https://dc.3.cn/category/get']

    def parse(self, response):
        item = Category()
        result = json.loads(response.body.decode("GBK"))
        data_list = result['data']
        for data in data_list:
            outer_cate = data['s'][0]
            outer_cate_info = outer_cate['n']
            item['outer_cate_title'], item['outer_cate_url'] = self.get_cate_name_url(outer_cate_info)
            middle_cate_list = outer_cate['s']
            for middle_cate in middle_cate_list:
                middle_cate_info = middle_cate['n']
                item['middle_cate_title'], item['middle_cate_url'] = self.get_cate_name_url(middle_cate_info)
                inner_cate_list = middle_cate['s']
                for inner_cate in inner_cate_list:
                    inner_cate_info = inner_cate['n']
                    item['inner_cate_title'], item['inner_cate_url'] = self.get_cate_name_url(inner_cate_info)
                    yield item

    def get_cate_name_url(self, category_info):
        '''
        根据分类信息提取分类名称和url
        :param category_info: 分类信息（大中小分类）
        :return: 名称和url
        '''
        cate_info_list = category_info.split('|')
        cate_url = cate_info_list[0]
        cate_title = cate_info_list[1]
        if 'jd.com' in cate_url:
            cate_url = 'https://' + cate_url
        elif cate_url.count('-') == 1:
            cate_url = 'https://channel.jd.com/{}.html'.format(cate_url)
        elif cate_url.count('-') == 2:
            cate_url = 'https://list.jd.com/list.html?cat={}'.format(cate_url.replace('-', ','))
        return cate_title, cate_url

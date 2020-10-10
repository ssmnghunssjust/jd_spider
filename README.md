## 项目未完成（目前爬取的是jd pc端网页的数据。PC端相比APP端来说更麻烦。）
## 本项目采取的是scrapy框架
## 类别和商品信息分开抓取
    * scrapy crawl jd_category
    * scrapy crawl jd_product
## 实现步骤
    * 根据需求，定义数据模型(items)
    * 实现分类爬虫(jd_category)
    * 保存分类信息(redis、pymongo)
    * 实现商品爬虫(jd_product)
    * 保存商品信息(pymongo)
    * 实现随机UA和代理IP下载器中间件，解决IP反爬(fake_useragent、ip代理池)
## 涉及的第三方库
    * 数据库
        * redis
        * pymongo
    * 分布式
        * scrapy_redis
    * 网络请求
        * requests
    * 重试
        * tenacity
    * 随机UA
        * fake_useragent
## 目前存在的反爬措施
    * referer
    * UA
    * cookie(不太重要)
    * IP频率
## 测试说明
    * 为了方便测试单个类别的商品爬取，这里只取了“超薄电视”类别作为目标列表页。（原因是，提取不同类别的列表页信息存在差异，也就是说超薄电视分类的代码不一定适用于其他分类）
    * 开启爬虫之前需要修改下载器中间件的ProxyMiddleware类，并在settings中开启该中间件。
    * 单个IP大约能爬取6000条商品信息，随即被封，大约3小时解封？（未经过详细测试）
## 商品类别样例
![Image](https://github.com/ssmnghunssjust/wenshu_retry/blob/main/img/pythonVersion.png)
## 商品爬取样例
```json
{
    "_id": ObjectId("5f815652705505ddff1ff63d"),
    "product_sku_id": "100011656748",
    "product_url": "https://item.jd.com/100011656748.html",
    "product_category": {
        "outer_cate_title": "家用电器",
        "outer_cate_url": "https://jiadian.jd.com",
        "middle_cate_title": "电视",
        "middle_cate_url": "https://list.jd.com/list.html?cat=737,794,798",
        "inner_cate_title": "超薄电视",
        "inner_cate_url": "https://list.jd.com/list.html?cat=737,794,798&ev=4155_76344&sort=sort_rank_asc&trans=1&JL=2_1_0#J_crumbsBar"
    },
    "product_title": "TCL 43V8  43英寸液晶电视机 4K超高清   超薄金属机身 全面屏 智慧屏 人工智能 教育电视 平板电视",
    "product_img_url": [
        "https://img13.360buyimg.com/n1/jfs/t1/131600/19/10017/99902/5f617e3aE7b0eaf7e/24a2841fa0ba55fb.jpg",
        "https://img13.360buyimg.com/n1/jfs/t1/97888/33/14714/239492/5e68e360Ea8819a27/52b002180db75d49.jpg",
        "https://img13.360buyimg.com/n1/jfs/t1/96228/37/14621/270064/5e68e360E3bbc4c5b/a68b4723464a10ee.jpg",
        "https://img13.360buyimg.com/n1/jfs/t1/106666/9/14788/215528/5e68e361E6012df26/6190fe279df83c74.jpg",
        "https://img13.360buyimg.com/n1/jfs/t1/100387/17/14972/206422/5e68e361E51caaa25/8f9d734699d45346.jpg",
        "https://img13.360buyimg.com/n1/jfs/t1/89934/17/14452/239248/5e68e361Eb3969117/a64aae2ce8f2ad80.jpg",
        "https://img13.360buyimg.com/n1/jfs/t1/103003/17/14635/28406/5e68e362E38842063/c0942799c288c5e1.jpg",
        "https://img13.360buyimg.com/n1/jfs/t1/92036/9/14809/105936/5e68e362Eef02bb32/cee34f782d87afa0.jpg"
    ],
    "product_shop": "TCL电视京东自营旗舰店",
    "product_option": [
        {
            "skuId": NumberLong("100011656748"),
            "尺寸": "AI声控智慧屏新品高配-43V8"
        },
        {
            "skuId": NumberLong("100014227820"),
            "尺寸": "4K+HDR金属智能新品-43L8"
        },
        {
            "skuId": NumberLong("100008129413"),
            "尺寸": "全高清全面屏智能新品-43V6F"
        },
        {
            "skuId": NumberLong("100014608268"),
            "尺寸": "全高清护眼智能电视-43L8F"
        },
        {
            "skuId": NumberLong("100013362476"),
            "尺寸": "全高清智能护眼全面屏-40V6F"
        },
        {
            "skuId": NumberLong("100007851453"),
            "尺寸": "全高清护眼智能电视-40L8F"
        },
        {
            "skuId": NumberLong("100013427834"),
            "尺寸": "高清智能护眼全面屏-32V6H"
        },
        {
            "skuId": NumberLong("100014577822"),
            "尺寸": "高清智能护眼电视-32L8H"
        },
        {
            "skuId": NumberInt("941189"),
            "尺寸": "高清蓝光护眼电视-L32F3301B"
        }
    ],
    "product_ad": "【TCL大牌钜惠】前200名超值抢购价1899元！咨询客服晒单加送269元延保一年！购机抽85吋电视！8K视频解码，AI免唤醒声控，健康防蓝光护眼",
    "product_price": "1899.00",
    "product_comments": {
        "comment_count": NumberInt("3791"),
        "default_good_count": NumberInt("1913"),
        "good_count": NumberInt("1860"),
        "good_rate": 0.99,
        "general_count": NumberInt("7"),
        "general_rate": 0.003,
        "poor_count": NumberInt("11"),
        "poor_rate": 0.007
    }
}
```
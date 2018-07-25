# -*- coding: utf-8 -*-

import scrapy
import urllib
import json
import re
from pyquery import PyQuery


class FangSpider(scrapy.Spider):
    name = 'fang'
    allowed_domains = ['wuhan.fang.com']
    start_urls = ['http://newhouse.wuhan.fang.com/house/s/']

    def parse(self, response):

        # 地区分类
        regions_list = response.xpath('//li[@id="quyu_name"]/a/@href').extract()[1:]

        for regions in regions_list:
            if regions:
                regions_url = urllib.parse.urljoin(response.url, regions)

                yield scrapy.Request(
                    regions_url,
                    callback=self.regional_housing
                )

            break  # 调试使用不需要循环多次, 关闭
        print('地区分类处理OK')

    def regional_housing(self, response):
        # print('查看楼盘请求完整的url: ', response.request.url)
        # print('查看楼盘响应完整的url: ', response.url)

        # 楼盘列表
        houses_list = response.xpath('//div[@class="nlc_img"]/a/@href').extract()
        for houses_url in houses_list:

            if houses_url:
                print('楼盘列表', houses_url)
                yield scrapy.Request(
                    houses_url,
                    callback=self.houses,
                    dont_filter=True
                )

            break  # 调试使用不需要循环多次, 关闭

        next_url = response.xpath('//a[@class="next"]/@href').extract_first()
        print('下一页: ', next_url)
        # 调试可注释,只是看看是否可获取就行了, 因为下一页的请求处理也是此函数
        # if next_url:
        #     next_url = urllib.parse.urljoin(response.url, next_url)
        #     yield scrapy.Request(
        #         next_url,
        #         callback=self.regional_housing
        #     )

    def houses(self, response):
        # # 用a标签取的问题
        # premises_details_url = response.xpath('//a[@id="xfptxq_B03_08"]/@href').extract_first()
        # if not houses_details_url:xfptxq_B03_08   xfptxq_B03_08
        #     houses_details_url = response.xpath('//a[@id="xfxq_B03_08"]/@href').extract_first()
        # if not houses_details_url:
        #     houses_details_url = response.xpath('//a[@id="xfsyxq_B03_02"]/@href').extract_first()

        houses_details_url = response.xpath('//div[@id="orginalNaviBox"]/a[2]/@href').extract_first()
        if houses_details_url:
            yield scrapy.Request(
                "http://guanggukejigang.fang.com/house/2611100908/housedetail.htm",
                callback=self.houses_details,
                dont_filter=True
            )

    def houses_details(self, response):

        print('查看楼盘详情请求完整的url路径: ', response.request.url)
        print('查看楼盘详情响应完整的url路径: ', response.url)

        item = dict()
        item['楼盘名称'] = response.xpath('//a[@class="ts_linear"]/@title').extract_first()
        item['楼盘价格'] = response.xpath('//div[@class="main-info-price"]/em/text()').extract_first().strip()

        facility = dict()
        facility_list = response.xpath('//ul[@class="sheshi_zb"]/li')
        if facility_list:
            for facility_xp in facility_list:
                facility_type = facility_xp.xpath('./span/text()').extract_first()
                facility[facility_type] = facility_xp.xpath('./text()').extract_first()
        else:
            # facility['设施'] = response.xpath('//div[@class="set bd-1"]/p').xpath('string(.)').\
            #     extract_first().strip().replace('\r\n', '')
            # print(facility['设施'])
            fa_str = response.xpath('//div[@class="set bd-1"]/p').extract_first()
            facility['设施'] = re.sub(r'\n', '; ', PyQuery(fa_str).text())

            # facility['交通'] = response.xpath('//div[@class="set "]').xpath('string(.)'). \
            #     extract_first().strip().replace(' ', '').replace('\r\n', '').replace('\n', '')
            tr_str = response.xpath('//div[@class="set "]').xpath('string(.)'). \
                extract_first().strip().replace(' ', '')
            facility['交通'] = re.sub(r'\n|\r\n', '', tr_str)
        item['周边设施'] = facility

        project = dict()
        project_list = response.xpath('//ul[@class="clearfix list"]/li')
        for project_xp in project_list:
            # project_type = project_xp.xpath('./div[1]/text()').extract()[0]
            project_type = project_xp.xpath('./div[1]').xpath('string(.)').extract_first().strip().replace(':', '')
            parameter_str = project_xp.xpath('./div[2]/text()').extract_first()
            if not parameter_str:
                parameter = project_xp.xpath('./div[2]/a/text()').extract_first().strip()
            else:
                parameter = parameter_str.strip()

            project[project_type] = parameter
        item['规划'] = project

        item['简介'] = response.xpath('//p[@class="intro"]/text()').extract_first().strip()

        # print(json.dumps(item, sort_keys=True, ensure_ascii=False, indent=4))
        yield item

# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest
import time
import json

class BilispiderSpider(scrapy.Spider):
    name = "bilispider"

    def start_requests(self):
        url_base = 'http://space.bilibili.com/ajax/member/GetInfo'
        for i in xrange(2, 300):
            yield FormRequest(url=url_base, 
                            formdata={'_' : str(int(time.time()*1000)),
                                        'mid' : str(i)},
                            headers={'Referer': 'http://space.bilibili.com'},
                            callback=self.parse)

    def parse(self, response):
        res_dict = json.loads(response.body_as_unicode())
        if res_dict['status'] == True:
            print res_dict['data']['name'], res_dict['data']['fans']

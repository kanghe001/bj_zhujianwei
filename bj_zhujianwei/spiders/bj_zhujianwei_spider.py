#!/usr/bin/env python
# coding=utf-8

import scrapy


class CrawlZhuJianWei(scrapy.Spider):
    name = "bj_zjw"
    start_urls = (
        'http://www.bjjs.gov.cn/tabid/3153/Default.aspx?ModelKey=FDCJY_HomePage_HousingManageList&projectID=5635926&systemID=2&srcId=1',
         )
    result = {}
    xiaoqu_detail = {}
    lou_detail = {}
    house_detail = {}


    # 将文件中所有url读取出来然后制作url
    def start_requests(self):
        f = file('/home/kanghe/all_url.txt', 'r')
        li = f.readlines()
        print li
        for url in li:
            yield self.make_requests_from_url(url.strip('\n'))

    def parse(self, response):
        print "first_url: " + response.url
        all_row = response.xpath('//td[@id="ess_ctr6854_ContentPane"]/div[1]/div[1]/table[2]/tr[2]/td/span/table/tr')
        for line in all_row:
            if line:
                value = line.xpath("td[2]/text()").extract_first()
                key = line.xpath("td[1]/text()").extract_first()
                self.xiaoqu_detail[key] = value

        detail_url = response.xpath('//table[@id="ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HomePage_HousingManageList_table_Buildinfo"]/tr/td[6]/a/@href').extract()
        for loupan_url_halt in detail_url:
            loupan_detail_url = response.urljoin(loupan_url_halt)
            yield scrapy.Request(loupan_detail_url, callback=self.loupan_detail)
        self.xiaoqu_detail.clear()

    def loupan_detail(self, response):
        loufang_num = response.xpath("//span[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_FloorInfo_Label_ProjectName']/text()").extract_first()
        if loufang_num:
            self.lou_detail["楼号"] = loufang_num

        useful_line = response.xpath("//table[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_FloorInfo_table_Buileing']/tr")[1:]
        for line in useful_line:
            each_danyuan_url = line.xpath("td/a/@href").extract()
            if each_danyuan_url:
                for half_url in each_danyuan_url:
                    next_url = response.urljoin(half_url)
                    print "kanghe: " + next_url
                    yield scrapy.Request(next_url, callback=self.danyuan_detail)
        self.lou_detail.clear()

    def danyuan_detail(self, response):

        info = response.xpath("//img[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HouseInfo_showImg']/@src").extract()[0]
        depart = response.xpath('//span[@id="ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HouseInfo_title"]/text()').extract()[0]
        if depart:
            self.house_detail["房间号"] = depart
            # self.result["房间号"] = depart
        eq_posi = info.index("=")
        info = info[eq_posi+1:]
        detail_list = info.split("$")
        if detail_list:
            for items in detail_list:
                self.house_detail[items.split("|")[0]] = items.split("|")[1]
        self.result.update(self.house_detail)
        self.result.update(self.lou_detail)
        self.result.update(self.xiaoqu_detail)
        yield self.result
        self.result.clear()
        self.house_detail.clear()

#!/usr/bin/env python
# coding=utf-8

import scrapy


class CrawlZhuJianWei(scrapy.Spider):
    name = "bj_zjw"
    start_urls = (
        'http://www.bjjs.gov.cn/tabid/3153/Default.aspx?ModelKey=FDCJY_HomePage_HousingManageList&projectID=5635926&systemID=2&srcId=1',
         )

    def __init__(self):
        super(CrawlZhuJianWei, self).__init__()
        self.result = {}
        self.xiaoqu_detail = {}
        self.lou_detail = {}
        self.house_detail = {}

    # 将文件中所有url读取出来然后制作url
    def start_requests(self):
        f = file('/home/kanghe/all_url.txt', 'r')
        li = f.readlines()
        print li
        for url in li:
            yield self.make_requests_from_url(url.strip('\n'))

    def parse(self, response):
        # print "first_url: " + response.url
        xiaoqu_detail = {}
        all_row = response.xpath('//td[@id="ess_ctr6854_ContentPane"]/div[1]/div[1]/table[2]/tr[2]/td/span/table/tr')
        for line in all_row:
            if line:
                value = line.xpath("td[2]/text()").extract_first()
                key = line.xpath("td[1]/text()").extract_first()
                xiaoqu_detail[key] = value

        detail_url = response.xpath('//table[@id="ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HomePage_HousingManageList_table_Buildinfo"]/tr/td[6]/a/@href').extract()
        for loupan_url_halt in detail_url:
            loupan_detail_url = response.urljoin(loupan_url_halt)
            # print "xiaoqu: "
            # print self.xiaoqu_detail
            yield scrapy.Request(loupan_detail_url, callback=lambda response=response, xiaoqu_detail=xiaoqu_detail:self.loupan_detail(response, xiaoqu_detail))

    def loupan_detail(self, response, xiaoqu_detail):
        lou_detail = {}
        loufang_num = response.xpath("//span[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_FloorInfo_Label_ProjectName']/text()").extract_first()
        if loufang_num:
            lou_detail["楼号"] = loufang_num
        else:
            lou_detail["楼号"] = " "

        useful_line = response.xpath("//table[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_FloorInfo_table_Buileing']/tr")[1:]
        for line in useful_line:
            each_danyuan_url = line.xpath("td/a/@href").extract()
            if each_danyuan_url:
                for half_url in each_danyuan_url:
                    next_url = response.urljoin(half_url)
                    # print "kanghe: ",
                    # print self.lou_detail
                    yield scrapy.Request(next_url, callback=lambda response=response, xiaoqu_detail=xiaoqu_detail, lou_detail=lou_detail: self.danyuan_detail(response, xiaoqu_detail, lou_detail))

    def danyuan_detail(self, response, xiaoqu_detail, lou_detail):
        house_detail = {}
        print "danyuan_url: ",
        print response.url
        # self.house_detail.clear()
        # print "self.house_detail: ",
        # print self.house_detail
        info = response.xpath("//img[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HouseInfo_showImg']/@src").extract()[0]
        depart = response.xpath('//span[@id="ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HouseInfo_title"]/text()').extract()[0]
        if depart:
            house_detail["房间号"] = depart
            # self.result["房间号"] = depart
        eq_posi = info.index("=")
        info = info[eq_posi+1:]
        detail_list = info.split("$")
        if detail_list:
            for items in detail_list:
                house_detail[items.split("|")[0]] = items.split("|")[1]
        print "合并之前house_detail\n"
        for key in house_detail:
            print key + ": ",
            print house_detail[key]
        print "合并之前lou_detail\n"
        for key in lou_detail:
            print key + ": ",
            print lou_detail[key]
        print "合并之前xiaoqu_detail\n"
        for key in xiaoqu_detail:
            print key + ": ",
            print xiaoqu_detail[key]
        print "合并之前result: ",
        print self.result
        self.result.update(xiaoqu_detail)
        self.result.update(lou_detail)
        self.result.update(house_detail)

        print "len(result): ",
        print len(self.result)
        for key in self.result:
            print str(key) + ":" + str(self.result[key]),
        print "all_detail: ",
        print self.house_detail, self.lou_detail, self.xiaoqu_detail
        yield self.result
        self.result.clear()


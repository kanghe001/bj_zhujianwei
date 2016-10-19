#!/usr/bin/env python
# coding=utf-8

import scrapy


class CrawlZhuJianWei(scrapy.Spider):
    name = "bj_zjw"
    start_urls = (
        'http://www.bjjs.gov.cn/tabid/3153/Default.aspx?ModelKey=FDCJY_HomePage_HousingManageList&projectID=5635926&systemID=2&srcId=1',
         )
    result = {}
    # result_keys = ["项目名称", "坐落位置", "开发企业", "预售许可证编号", "发证日期", "预售登记备案管理部门",
    #            "建设工程规划许可证编号", "土地用途和使用年限", "准许销售面积", "批准预售部位", "预售资金监管银行", "专用账户名称",
    #           "专用账户账号", "楼号", "规划设计用途", "户型", "建筑面积", "套内面积", "按建筑面积拟售单价", "按套内面积拟售单价",
    #          ]
    num = 0
    project_name = ""
    loacation = ""
    developer = ""
    ys_num = ""
    issue_date = ""
    confirm_com = ""
    contruct_allowed_num = ""
    use_time = ""
    allow_area = ""
    allow_sale_part = ""
    bank = ""
    account_name = ""
    account_num = ""
    result_value = []

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
                self.result[key] = value

        """
        self.project_name = all_row[0].xpath("td[2]/text()").extract_first()
        self.loacation = all_row[1].xpath("td[2]/text()").extract_first()
        self.developer = all_row[2].xpath("td[2]/text()").extract_first()
        self.ys_num = all_row[3].xpath("td[2]/text()").extract_first()
        self.issue_date = all_row[4].xpath("td[2]/text()").extract_first()
        self.confirm_com = all_row[5].xpath("td[2]/text()").extract_first()
        self.contruct_allowed_num = all_row[6].xpath("td[2]/text()").extract_first()
        self.use_time = all_row[7].xpath("td[2]/text()").extract_first()
        self.allow_area = all_row[8].xpath("td[2]/text()").extract_first()
        self.allow_sale_part = all_row[9].xpath("td[2]/text()").extract_first()
        self.bank = all_row[10].xpath("td[2]/text()").extract_first()
        self.account_name = all_row[11].xpath("td[2]/text()").extract_first()
        self.account_num = all_row[12].xpath("td[2]/text()").extract_first()


        pause = [self.project_name, self.loacation, self.developer, self.ys_num, self.issue_date, self.confirm_com,
                 self.contruct_allowed_num, self.use_time, self.allow_area, self.allow_sale_part, self.bank,
                 self.account_name, self.account_num
                 ]
        self.result_value.extend(pause)
        """

        detail_url = response.xpath('//table[@id="ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HomePage_HousingManageList_table_Buildinfo"]/tr/td[6]/a/@href').extract()
        for loupan_url_halt in detail_url:
            loupan_detail_url = response.urljoin(loupan_url_halt)
            yield scrapy.Request(loupan_detail_url, callback=self.loupan_detail)

    def loupan_detail(self, response):
        loufang_num = response.xpath("//span[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_FloorInfo_Label_ProjectName']/text()").extract_first()
        if loufang_num:
            self.result["楼号"] = loufang_num

        useful_line = response.xpath("//table[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_FloorInfo_table_Buileing']/tr")[1:]
        for line in useful_line:
            each_danyuan_url = line.xpath("td/a/@href").extract()
            if each_danyuan_url:
                for half_url in each_danyuan_url:
                    next_url = response.urljoin(half_url)
                    print "kanghe: " + next_url
                    yield scrapy.Request(next_url, callback=self.danyuan_detail)

    def danyuan_detail(self, response):
        info = response.xpath("//img[@id='ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HouseInfo_showImg']/@src").extract()[0]
        depart = response.xpath('//span[@id="ess_ctr6854_FDCJY_SSHouse_Model_FDCJY_HouseInfo_title"]/text()').extract()[0]
        if depart:
            self.result["房间号"] = depart
        eq_posi = info.index("=")
        info = info[eq_posi+1:]
        detail_list = info.split("$")
        if detail_list:
            for items in detail_list:
                self.result[items.split("|")[0]] = items.split("|")[1]
        yield self.result
        self.result.clear()





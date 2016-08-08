# -*- coding: utf-8 -*-

import scrapy
from scrapy import exceptions
from scraper.items import ResolutionItem


class ResolutionSpider(scrapy.Spider):
    """government resolutions spider using session data provided by pmo.gov.il website."""
    name = "resolutions"
    allowed_domains = ["www.pmo.gov.il"]

    start_urls = ["http://www.pmo.gov.il/Secretary/GovDecisions/Pages/default.aspx?PN=1"]

    # this is the form variable that needs to be set
    # in a gov. resolution form request,
    # in order to receive resolutions for a specific government number
    #
    # this var name looks like it was randomly chosen,
    # but in fact it is constant and doesn't change
    #
    # the '%d' at the end should be set to integers 0-6
    # in order to specifiy the government number that the form requests
    #
    # the value of this header should be "on"
    gov_number_header_key = (
        "ctl00"
        "$ctl20$g_35b6db55_6fcf_4f5a_8632_254e3865d040$ctl00$cblGovernments"
        "$%d"
    )
    gov_number_header_value = "on"

    def __init__(self,
                 # government numbers to scrape
                 # 0-6 are all available governments
                 gov_indexes="0,1,2,3,4,5,6",
                 *args, **kwargs):

        super(ResolutionSpider, self).__init__(*args, **kwargs)

        # convert gov. indexes string to integer list
        self.gov_indexes = [int(i) for i in gov_indexes.split(',')]

        # validate values
        for i in self.gov_indexes:
            if i < 0 or i > 6:
                raise exceptions.CloseSpider(
                    "gov_indexes list can only include integers ranging 0-6")

    def parse(self, response):
        """submit a gov. resolution form for every gov. number and parse

        there are 6 available governments, and their buttons are numbered 0 to 5.
        this submits a form for each government separately,
        since the gov. resolutions websites tends to get overloaded
        and stop responding very quickly.
        """
        # iterate over given gov. indexes
        # and scrape each one
        for i in self.gov_indexes:
            # submit form request,
            # requesting all pages from given government number
            # using previously received session headers
            yield FormRequest.from_response(
                response,
                formdata={self.gov_number_header_key % i: self.gov_number_header_value},
                callback=self.parse_form_result)

    def parse_form_result(self, response):
        """parse resolution list page."""
        # parse resolutions found in current page
        for sel in response.xpath("//div[@id='GDSR']/div/a/@href"):
            yield scrapy.Request(sel.extract(),
                                 callback=self.parse_resolution)

        # parse next pages
        # requires reusing (session) headers in order to keep form results
        # for current government.
        # otherwise the default results are returned, which are the latest 10
        # resolutions from the current government.
        for sel in response.xpath("//a[@class='PMM-resultsPagingNumber']/@href"):
            url = response.urljoin(sel.extract())
            yield scrapy.Request(url,
                                 headers=response.headers,
                                 callback=self.parse_form_result)

    def parse_resolution(self, response):
        """parse specific resolution page."""
        try:
            yield ResolutionItem(
                url=response.url,
                date=response.xpath("/html/head/meta[@name='EventDate']/@content").extract(),
                resolution_number=response.xpath("//*[@id='aspnetForm']/@action").extract(),
                gov=response.xpath("/html/head/meta[@name='Subjects']/@content").extract(),
                title=response.xpath("//h1[@class='mainTitle']//text()").extract(),
                subject=response.xpath("//div[@id='ctl00_PlaceHolderMain_GovXParagraph1Panel']//text()[not(ancestor::h3)]").extract(),
                body=response.xpath("//*[@id='ctl00_PlaceHolderMain_GovXParagraph2Panel']//text()[not(ancestor::h3)]").extract(),
            )
        except AttributeError:
            self.logger.error('bad body in response for url %s and body %s',
                              response.url, response.body)

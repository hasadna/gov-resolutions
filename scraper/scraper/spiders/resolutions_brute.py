# -*- coding: utf-8 -*-

import itertools as it

import scrapy

from scraper.items import ResolutionItem

def _generate_urls():
    """generate all possible start_urls combinations.

    resolutions come in all kinds of weird incosistent forms:
    dec1, des1, dess1, desi1, desr1, desR1, des1R, etc.

    this returns a cartesian product on all *possible* combinations.

    NOTE most combinations will yield a 'HTTP 404 Not Found' result.
    Still, this is still a faster way then submitting forms
    and paginating the stateful gov resolutions website.
    """
    for year in reversed(range(2001, 2017)):
        for prefix, res_num, postfix in it.product(
                ['dec', 'decH', 'deci', 'decR',
                 'des', 'desr', 'dess',
                 'r', 'spoke',
                ],
                range(2000),
                ['', 'R'],
            ):

            resolution = ''.join([prefix, str(res_num), postfix])

            yield "http://www.pmo.gov.il/Secretary/GovDecisions/%s/Pages/%s.aspx" % (
                year, resolution)


class ResolutionBruteSpider(scrapy.Spider):
    """brute force try all possible resolution combinations urls.

    this is different the ResolutionsSpider in that it doesn't perform pagination.
    see _generate_urls for more info.
    """
    name = "resolutions_brute"
    allowed_domains = ["www.pmo.gov.il"]
    start_urls = _generate_urls()

    def should_retry(self, response):
        """Sometimes body uses anti-scraping tricks.

        e.g. body is:
        <html><body><script>document.cookie='yyyyyyy=ea850ff3yyyyyyy_ea850ff3; path=/';window.location.href=window.location.href;</script></body></html>

        Retrying usually yields a correct response.
        """
        if response.status == 404:
            return False
        if not response.body.startswith('<html><body><script>'):
            return False

        self.logger.debug('anti-scraping trick for url %s', response.url)

        new_request = response.request.copy()
        new_request.dont_filter = True  # don't de-duplicate the url for retrying

        return new_request

    def parse(self, response):
        """Scrape relevant fields in specific resolution response."""
        # check if response was bad
        new_request = self.should_retry(response)
        # retry if so
        if new_request:
            yield new_request
            return

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


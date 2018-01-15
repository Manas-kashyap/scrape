# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from dateutil import parser


class NdtvSpider(scrapy.Spider):
    name = 'ndtv'
    custom_settings = {
        'site_id': 104,
        'site_name': 'NDTV',
        'site_url': 'https://www.ndtv.com/latest/page-1'}
    download_delay = 2

    def __init__(self, pages=3, *args, **kwargs):
        super(NdtvSpider, self).__init__(*args, **kwargs)
        self.pages = pages
        for count in range(0, int(pages)):
            self.start_urls.append('http://www.ndtv.com/latest/page-' + str(count + 1))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        logger.error(__name__ + ' Non-200 Response Received at ' + str(failure.request.url))

    def parse(self, response):
        for article_url in response.xpath('//div[@class="nstory_header"]/a/@href').extract():
            self.urls_parsed += 1
            yield scrapy.Request(url=article_url, callback=self.parse_article, errback=self.errorRequestHandler)

    def parse_article(self, response):
        try:
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.parse_image(response)
            item['title'] = self.parse_title(response)
            item['content'] = self.parse_content(response)
            item['link'] = response.url
            item['newsDate'] = str(self.parse_date(response))
            item['source'] = 104
            if item['image'] is not None and item['title'] is not None and item['content'] is not None and item['newsDate'] is not None:
                self.urls_scraped += 1
                yield item
            else:
                self.urls_dropped += 1
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)

    def parse_image(self, response):
        try:
            if 'gadgets.ndtv.com' in response.url:
                return response.xpath('//div[@class="fullstoryImage"]/picture/source/@srcset').extract_first()
            elif 'www.ndtv.com' in response.url:
                return response.xpath('//div[contains(@class, "ins_mainimage_big")]/img/@src').extract_first()
            elif 'auto.ndtv.com' in response.url:
                return response.xpath('//img[@itemprop="url"]/@src').extract_first()
            elif 'food.ndtv.com' in response.url:
                return response.xpath('//div[@itemprop="image"]/meta[@itemprop="url"]/@content').extract_first()
            elif 'sports.ndtv.com' in response.url:
                return response.xpath('//div[@itemprop="image"]/img[@class="caption"]/@src').extract_first()
            elif 'doctor.ndtv.com' in response.url:
                return response.xpath('//div[@class="article-stry-image"]/img/@src').extract_first()
            elif 'profit.ndtv.com' in response.url:
                return response.xpath('///div[@id="story_pic"]/div/img/@src').extract_first()
            else:
                logger.error(__name__ + ' Unable to Extract Image : ' + response.url)
                return None
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Image : " + str(e) + " : " + response.url)
            return None

    def parse_title(self, response):
        try:
            if 'gadgets.ndtv.com' in response.url:
                return response.xpath('//div[@class="lead_heading"]/h1/span/text()').extract_first().strip()
            elif 'www.ndtv.com' in response.url or 'food.ndtv.com' in response.url:
                return response.xpath('//h1[@itemprop="headline"]/text()').extract_first().strip()
            elif 'sports.ndtv.com' in response.url or 'profit.ndtv.com' in response.url:
                return response.xpath('//h1[@itemprop="headline"]/text()').extract_first().strip()
            elif 'auto.ndtv.com' in response.url:
                return response.xpath('//h1[@class="article__headline"]/text()').extract_first()
            elif 'doctor.ndtv.com' in response.url:
                return response.xpath('//div[contains(@class, article_heading)]/div[@class="__sslide"]/h1/text()').extract_first().strip()
            else:
                logger.error(__name__ + ' Unable to Extract Image ' + response.url)
                return None
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Title : " + str(e) + " : " + response.url)
            return None

    def parse_content(self, response):
        try:
            content = ''
            if 'gadgets.ndtv.com' in response.url:
                content_fragmented = response.css('div.content_text>p::text').extract()
                for c in content_fragmented:
                    content += c.strip()
            elif 'www.ndtv.com' in response.url:
                content_fragmented = response.xpath('//div[@itemprop="articleBody"]/text()').extract()
                for c in content_fragmented:
                    content += c.strip()
            elif 'auto.ndtv.com' in response.url or 'sports.ndtv.com' in response.url:
                content_fragmented = response.xpath('//div[@itemprop="articleBody"]/p/text()').extract()
                for c in content_fragmented:
                    content += c.strip()
            elif 'food.ndtv.com' in response.url or 'profit.ndtv.com' in response.url:
                content_fragmented = response.xpath('//span[@itemprop="articleBody"]/text()').extract()
                for c in content_fragmented:
                    content += c.strip()
            elif 'doctor.ndtv.com' in response.url:
                content_fragmented = response.xpath('//div[@class="article_storybody"]/p/text()').extract()
                for c in content_fragmented:
                    content += c.strip()
            else:
                logger.error(__name__ + ' Unable to Extract Image ' + response.url)
                return None
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to extract Image")
            return None
        return content.strip()

    def parse_date(self, response):
        try:
            date = ''
            if 'www.ndtv.com' in response.url:
                date = response.xpath('//meta[@name="modified-date"]/@content').extract_first()[:-6]
            elif 'doctor.ndtv.com' in response.url or 'sports.ndtv.com' in response.url:
                date = response.xpath('//meta[@name="publish-date"]/@content').extract_first()[:-6]
            elif 'auto.ndtv.com' in response.url:
                date = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()[:-6]
            elif 'food.ndtv.com' in response.url:
                date = response.xpath('//span[@itemprop="dateModified"]/@content').extract_first()[:-6]
            elif 'gadgets.ndtv.com' in response.url or 'profit.ndtv.com' in response.url:
                date = response.xpath('//meta[@name="publish-date"]/@content').extract_first()[:-6]
            else:
                logger.error(__name__ + ' Unable to Extract Date ' + response.url)
                return None

            date = (parser.parse(date)).strftime('%Y-%m-%dT%H:%M:%S')

        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to extract Date : " + str(e) + " : " + response.url)
            return None
        
        return date

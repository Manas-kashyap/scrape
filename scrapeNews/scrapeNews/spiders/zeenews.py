# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from datetime import datetime


class zeespider(scrapy.Spider):
    name = "zee"
    start_urls = ['http://zeenews.india.com/india',]
    custom_settings = {
        'site_id':106,
        'site_name':'Zee News',
        'site_url':'http://zeenews.india.com/india'}

    #Scraping the main page for article links
    def parse(self, response):
        try:
            articles = response.xpath('//section[contains(@class, "maincontent")]//div[contains(@class, "section-article")]') #extracts HTML from the start_url
            #Scrapes columns of articles
            for article in articles:
                x = article.xpath('.//h3/a[2]') #extracts <a> tag from start _url
                link = x.xpath('.//@href').extract_first()  #extracts URL for the articles recursively
                self.urls_parsed += 1
                yield response.follow(link, callback = self.parse_news)
            
            #For scraping the links on the next page of the website
            next_page = response.xpath('//link[@rel = "next"]/@href').extract_first()
            if next_page is not None:
            logger.info(__name__ + " ==============Switching Page======================")
            yield response.follow(next_page, callback = self.parse)
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)

    #For scraping a particular article listed on the main page
    def parse_news(self,response):
        try:
            i = ScrapenewsItem()
            i['title'] =  self.gettitle(response)   #scrapes headline
            i['newsDate'] = self.getdatetime(response)  #scrapes date
            i['image'] = self.getimage(response)    #scrapes image link
            i['content'] = self.getcontent(response)    #scrapes content
            i['link'] = response.url    #scrapes link 
            i['source'] = 106   #database entry

            flag = 0
            for x in i:
                if i[x] == 'Error':
                    self.urls_dropped += 1
                    flag = 1
                    yield None
                    break
            if flag == 0:
                self.urls_scraped += 1
                yield i
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)
            yield None
         
    def gettitle(self,response):
        try:
            data = response.xpath('//h1[contains(@class, "article-heading margin")]/text()').extract_first() 
            if (data is None):
                logger.error(__name__ + " Unable to Extract Title : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Title : " + str(e) + " : " + response.url)
            data = 'Error'
        return data   

    def getdatetime(self,response):
        try:
            data = response.xpath('//span[contains(@class, "date")]/text()').extract_first()[10:-4] 
            z = (datetime.strptime(data," %b %d, %Y, %H:%M %p")).strftime("%Y-%m-%d %H:%M:%S")  
            if (z is None):
                logger.error(__name__ + " Unable to Extract Title : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Date : " + str(e) + " : " + response.url)
            data = 'Error'
        return data   

    def getcontent(self,response):
        try:
            data = response.xpath('//div[contains(@class, "article")]/div[contains(@class, "field")]//p/text()').extract()
            if (data is None):
                logger.error(__name__ + " [UNHANDLED] Unable to Extract Title : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Content : " + str(e) + " : " + response.url)
            data = 'Error'
        return data

    def getimage(self,response):
        try:
            data = response.xpath('//div[contains(@class, "field-item")]/img/@src').extract_first() #scrapes image url
            if (data is None):
                logger.error(__name__ + " Unable to Extract Image : " + str(e) + " : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Image : " + str(e) + " : " + response.url)
            data = 'Error'
        return data
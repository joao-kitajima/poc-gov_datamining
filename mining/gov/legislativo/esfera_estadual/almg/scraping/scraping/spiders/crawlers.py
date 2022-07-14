import scrapy


class AlmgCrawler(scrapy.Spider):
    name = 'almg_crawler'
    start_urls = ['https://www.al.sp.gov.br/dados-abertos/']
    
    
    def parse(self, response):
        for anchor in response.xpath('//div[@id="myCarousel"]/descendant::a[not(contains(@class, "carousel-control"))]'):
            link = anchor.xpath('@href').get().split(';')[0].strip('/dados-abertos')
            
            yield response.follow(link, callback=self.parse_links)


    def parse_links(self, response):
        for anchor in response.xpath('//legend/a'):
            link = anchor.xpath('@href').get()
            
            yield response.follow(link, callback=self.parse_item)
            
    
    def parse_item(self, response):
        url = response.xpath('//td[not(contains(@id, "icones"))]/a/@href').get()
         
        yield {
            'name': response.xpath('//div[@class="titulo_grupo"]/h1/text()').get(),
            'description': response.xpath('//div[@id="grupos"]/descendant::p[2]/text()').get(), 
            'url': url
        }

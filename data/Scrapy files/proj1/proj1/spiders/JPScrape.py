import scrapy
from proj1.items import Proj1Item

class JPScrape(scrapy.Spider):
	name = 'proj1'
	start_urls = ['https://stackoverflow.com/questions/tagged/python?page=40&sort=votes&pagesize=50']

	def parse(self, response):
		# get link to a question page
		for shopName in response.css('div.summary > h3'):
			yield response.follow(shopName.css('a ::attr(href)').extract_first(), self.parse2)

		# go to next page
		for next_page in response.css('div.pager.fl > a[rel = "next"]'):
			yield response.follow(next_page, self.parse)

	# runs on a ques page
	def parse2(self,response):
		item = Proj1Item()
		
		item['posts'] = ['0','1']

		# get question text
		for s in response.css('td.postcell > div '):
			result = s.css('div.post-text').extract_first()
			item['posts'][0] = result
			
		# get answer text
		for s in response.css('td.answercell > div.post-text'):
			result = s.css('div.post-text').extract_first()
			item['posts'][1] = result
			break;
			
		yield item	
		
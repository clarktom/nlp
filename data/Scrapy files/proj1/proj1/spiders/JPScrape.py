import scrapy
from proj1.items import Proj1Item

class JPScrape(scrapy.Spider):
	name = 'proj1'
	start_urls = ['https://stackoverflow.com/questions/tagged/python?page=80&sort=votes&pagesize=50']

	def parse(self, response):
		# get link to a question page1
		for firstLink in response.css('div.summary > h3'):
			yield response.follow(firstLink.css('a ::attr(href)').extract_first(), self.parse2)

		# go to next page
		for next_page in response.css('div.pager.fl > a[rel = "next"]'):
			yield response.follow(next_page, self.parse)

	# runs on a ques page
	def parse2(self,response):
		item = Proj1Item()
		item['answers'] = []
		item['numOfAns']=0
		# get question text
		for s in response.css('td.postcell > div '):
			result = s.css('div.post-text').extract_first()
			item['question'] = result
		# get answer text
		for s in response.css('td.answercell > div.post-text'):
			result = s.css('div.post-text').extract_first()
			item['answers'].append(result)
			item['numOfAns'] = item['numOfAns'] + 1
            
		if(item['numOfAns'] == 30):
			yield 
		else:
			yield item
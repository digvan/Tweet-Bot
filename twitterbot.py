from urllib2 import urlopen
from random import choice
import redis,twitter,json,bitly

BITLY_API = 'YOUR BITLY API'
USERNAME = "YOUR TWITTER USERNAME"
PASSWORD = "YOUR TWITTER PASSWORD"
RSS = "YOUR RSS URL from YQL -- output JSON FORMAT"

R = redis.Redis('localhost')
print 
class News(object):
	''' The current Purdue engineering news get by rss'''
	def __init__(self):
		self.ReterieveNews()

	def ReterieveNews(self):
		''' Returns the current new News.'''
		url_obj = urlopen(RSS)
		json_obj = json.loads(url_obj.read())
		for item in json_obj["query"]["results"]["item"]:
			link = item["link"]
			title = item["title"]
			pubdate = item["pubDate"]
			self.AddNews(title,pubdate,link)		
	def AddNews(self,title,pubdate,link):
		if R.sadd("titles", title):
			R.hset('news:%s' %title,'pubdate', pubdate)
			R.hset('news:%s' %title,'title', title)
			R.hset('news:%s' %title,'link', link)			
			return True
		else:
			return False
	def GetNewNews(self):
		# get not posted news from DB
		return_list = []
		not_posted_set = R.sdiff(["titles","posts"])
		for item in not_posted_set:
			long_link = R.hget('news:%s' %item,'link')
			short_link = self.ShortURL(long_link)
			text = item + "  " + short_link
			if len(text) > 140:
				text = item[0:125] + "..." + short_link
			d = {"text":text ,"title":item}
			return_list.append(d)
		return return_list
	def post(self):
		# add posted item to the posts set
		self.API = twitter.Api(username = USERNAME, password = PASSWORD)
		list = self.GetNewNews()
		if len(list) == 0:
			print "no not new posted news."
			return
		for item in list:
			print item["text"]
			print "Posting...."
			self.API.PostUpdate(item["text"])
			print "Done!"
			R.sadd("posts",item["title"])
	def ShortURL(self,url):
		 api = bitly.Api(login="BITLY UERNAME",apikey=BITLY_API)
		 short = api.shorten(url,{'history':1})
		 return short
if __name__ == '__main__':
	n = News()
	n.post()
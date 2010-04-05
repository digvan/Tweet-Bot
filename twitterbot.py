from urllib2 import urlopen
from random import choice
import redis,twitter,json,bitly

import gdata.youtube
import gdata.youtube.service

YOUTUBE_API = 'YOUR YOUTUBE DEVELOPER KEY'
YOUTUBE_USERNAME_OF_RET = "USERNAME OF WHO YOU WANT TO DOWNLOAD HIS/HER FEED"
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
		self.RetVideos()
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
	def PostNews(self):
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
	def RetVideos(self):
		yt_service = gdata.youtube.service.YouTubeService()
		yt_service.developer_key = YOUTUBE_API
		uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % YOUTUBE_USERNAME_OF_RET
		feed = yt_service.GetYouTubeVideoFeed(uri)
		for entry in feed.entry:
			title = entry.media.title.text
			pubdate = entry.published.text
			link = entry.media.player.url
			self.AddVideo(title,pubdate,link)
	def AddVideo(self,title,pubdate,link):
		if R.sadd("vidtitles", title):
			R.hset('videos:%s' %title,'pubdate', pubdate)
			R.hset('videos:%s' %title,'title', title)
			R.hset('videos:%s' %title,'link', link)			
			return True
		else:
			return False
	def GetNewVideo(self):
		# get not posted news from DB
		return_list = []
		not_posted_set = R.sdiff(["vidtitles","vidposts"])
		for item in not_posted_set:
			long_link = R.hget('videos:%s' %item,'link')
			short_link = self.ShortURL(long_link)
			text = item + "  " + short_link + " #Purdue"
			if len(text) > 140:
				text = item[0:125] + "..." + short_link + " #Purdue"
			d = {"text":text ,"title":item}
			return_list.append(d)
		return return_list			
	def PostVideo(self):
		self.API = twitter.Api(username = USERNAME, password = PASSWORD)
		list = self.GetNewVideo()
		if len(list) == 0:
			print "no new posted videos."
			return
		for item in list:
			print item["text"]
			print "Posting...."
			self.API.PostUpdate(item["text"])
			print "Done!"
			R.sadd("posts",item["title"])
if __name__ == '__main__':
	n = News()
	n.PostNews()
	n.PostVideo()
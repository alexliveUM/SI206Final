from requests_oauthlib import OAuth1
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
import json
import sys
import requests
import secrets

#Code for OAuth starts
class Tweet:
	def __init__(self, tweet_dict_from_json):
		self.is_retweet = False
		self.text = tweet_dict_from_json['text']
		self.username = tweet_dict_from_json['user']['screen_name']
		self.creation_date = tweet_dict_from_json['created_at']
		self.num_retweets = tweet_dict_from_json['retweet_count']
		self.num_favorites = tweet_dict_from_json['favorite_count']
		self.id = tweet_dict_from_json['id']
		self.popularity_score = self.num_retweets * 2 + self.num_favorites * 3

	def __str__(self):
		return '@{}: {}\n[retweeted {} times]\n[favorited {} times]\n[popularity {}]\n[tweeted on {} | id:{}]\n'.format(self.username, self.text, self.num_retweets, self.num_favorites, self.popularity_score, self.creation_date, self.id)

class Searchable:
	def __init__(self):
		self.conn = sqlite3.connect(DBNAME)
		self.url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
		self.auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
		self.requests.get(url, auth=auth)

	def get_restaurant_tweets(self, key,count=50):
		results = []
		base_url = 'https://api.twitter.com/1.1/search/tweets.json'
		content = ''
		if False: #key in cache:
			printd('$$$ {} $$$'.format(key))
			content = cache[key]
		else:
			# oauth
			printd('@@@ OAuth @@@')
			url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
			auth = OAuth1(secrets.twitter_api_key, secrets.twitter_api_secret, secrets.twitter_access_token, secrets.twitter_access_token_secret)
			requests.get(url, auth=auth)
			# request
			printd('@@@ Requesting {} @@@'.format(key))
			params = {
				'q':key.lower(),
				'count':count
			 }
			response = requests.get(base_url, auth=auth, params=params)
			content = response.text
		data = json.loads(content)
		printd('Tweets fetched: {}'.format(len(data['statuses'])))
		for tweet in data['statuses']:
			if 'rt' not in tweet['text'].lower():
				results.append(Tweet(tweet))
			if len(results) == 10:
				break
		# cache bookkeeping
		cache['update'] = True
		cache[key] = content
		writeToCache(cache, cache_str)
		# sort results
		sorted_results = sorted(results, key=lambda x: x.popularity_score, reverse=True)
		return sorted_results


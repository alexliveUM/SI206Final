from requests_oauthlib import OAuth1
import json
import sqlite3
import sys
import requests
import secrets

consumer_key = secrets.api_key
consumer_secret = secrets.api_secret
access_token = secrets.access_token
access_secret = secrets.access_token_secret

#Code for OAuth starts
class Tweet:
	def __init__(self, restaurant_id, tweet_dict_from_json=None, db_line=None):
		self.restaurant_id = restaurant_id
		if tweet_dict_from_json:
			self.text = tweet_dict_from_json['text'].replace('"', "'")
			self.username = tweet_dict_from_json['user']['screen_name']
			self.creation_date = tweet_dict_from_json['created_at']
			self.num_retweets = tweet_dict_from_json['retweet_count']
			self.num_favorites = tweet_dict_from_json['favorite_count']
			self.id = tweet_dict_from_json['id']
			self.popularity_score = self.num_retweets * 2 + self.num_favorites * 3 
		else:
			self.text = db_line[3]
			self.username = db_line[2]
			self.creation_date = db_line[4]
			self.num_retweets = db_line[5]
			self.num_favorites = db_line[6]
			self.id = db_line[0]
			self.popularity_score = db_line[7]

	def __str__(self):
		return '@{}: {}\n[retweeted {} times]\n[favorited {} times]\n[popularity {}]\n[tweeted on {} | id:{}]\n'.format(self.username, self.text, self.num_retweets, self.num_favorites, self.popularity_score, self.creation_date, self.id)

	def insert_str(self, cur):
		cur.execute('INSERT INTO "Tweets" VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (self.id, self.restaurant_id, self.username, self.text, self.creation_date, self.num_retweets, self.num_favorites, self.popularity_score))

class Twitter:
	def __init__(self):
		self.url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
		self.auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
		requests.get(self.url, auth=self.auth)
		self.conn = sqlite3.connect('SI206DB.db')
		
	def writeToCache(self, data):
		print('### Updating TWEETS cache ###')
		cache_obj = open('cache/TWEETS.txt', 'w')
		json.dump(data, cache_obj, indent=2)
		print('### Cache updated to {} items ###'.format(len(data)))
		cache_obj.close()

	def check_db(self, key):
		cur = self.conn.cursor()
		cur.execute('SELECT * FROM Tweets WHERE RestaurantId="{}" ORDER BY "Score" DESC'.format(key.id))
		results = cur.fetchall()
		cache = []
		for result in results:
			cache.append(Tweet(key.id, db_line=result))
		return cache

	def get_restaurant_tweets(self, key, count=25, reset=False):
		# load existing tweets for restaurant
		results = self.check_db(key)
		base_url = 'https://api.twitter.com/1.1/search/tweets.json'
		cache = {}
		try:
			file_obj = open('cache/TWEETS.txt', 'r')
			file_data = file_obj.read()
			cache = json.loads(file_data)
			file_obj.close()
		except:
			pass
		cur = self.conn.cursor()
		if reset == True or len(results) == 0:
			# request
			print('@@@ TWEET: Requesting {} @@@'.format(key.name.lower()))
			params = {
				'q': key.name.lower(),
				'count': 50
			}
			response = requests.get(base_url, auth=self.auth, params=params)
			data = json.loads(response.text)
			# results = list of Tweets, valid_tweets = list of tweet objects for cache
			print('Tweets fetched: {}'.format(len(data['statuses'])))
			results = []
			valid_tweets = []
			for el in data['statuses']:
				if 'rt' not in el['text'].lower():
					valid_tweets.append(el)
					results.append(Tweet(key.id, tweet_dict_from_json=el))
					print(results[-1].id)
				if len(results) == count:
					break
			# add to cache
			cache[key.id] = valid_tweets
			# update cache & db
			self.writeToCache(cache)
			# clear out stale tweets
			cur.execute('DELETE FROM Tweets WHERE RestaurantId=?',(key.id,))
			for result in results:
				try:
					result.insert_str(cur)
				except:
					pass
			self.conn.commit()
		else:
			results = results[0:count]
		# sort results
		sorted_results = sorted(results, key=lambda x: x.popularity_score, reverse=True)
		return sorted_results

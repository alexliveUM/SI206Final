from requests_oauthlib import OAuth1
import nltk
import json
import sys
import requests
import secret_data 

consumer_key = secret_data.api_key
consumer_secret = secret_data.api_secret
access_token = secret_data.access_token
access_secret = secret_data.access_token_secret

#Code for OAuth starts
class Tweet:
	def __init__(self, tweet_dict_from_json):
		self.text = tweet_dict_from_json['text']
		self.username = tweet_dict_from_json['user']['screen_name']
		self.creation_date = tweet_dict_from_json['created_at']
		self.num_retweets = tweet_dict_from_json['retweet_count']
		self.num_favorites = tweet_dict_from_json['favorite_count']
		self.id = tweet_dict_from_json['id']
		self.popularity_score = self.num_retweets * 2 + self.num_favorites * 3

	def __str__(self):
		return '@{}: {}\n[retweeted {} times]\n[favorited {} times]\n[popularity {}]\n[tweeted on {} | id:{}]\n'.format(self.username, self.text, self.num_retweets, self.num_favorites, self.popularity_score, self.creation_date, self.id)

class Twitter:
	def __init__(self):
		self.url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
		self.auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
		self.requests.get(url, auth=auth)

	def get_restaurant_tweets(self, key,count=50):
		cache = fetchCache()
		results = []
		base_url = 'https://api.twitter.com/1.1/search/tweets.json'
		content = ''
		if len(cache): #key in cache:
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

if __name__ == "__main__":
	if not consumer_key or not consumer_secret:
		print("You need to fill in client_key and client_secret in the secret_data.py file.")
		exit()
	if not access_token or not access_secret:
		print("You need to fill in this API's specific OAuth URLs in this file.")
		exit()

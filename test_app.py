import twitter
import yelp
import os
import sqlite3
import json
import sys
import requests
import secrets
import init_db
import unittest

# class mimicing yelp.Restaurant
class FakeRestaurant:
	def __init__(self, id, name):
		self.id = id
		self.name = name

class TestApp(unittest.TestCase):

	def test_db(self):
		# create db
		init_db.run()
		self.assertTrue(os.path.exists('SI206DB.db'))
		conn = sqlite3.connect('SI206DB.db')
		cur = conn.cursor()
		# check if tables exist
		cur.execute('SELECT COUNT(*) FROM Tweets')
		self.assertTrue(0 == cur.fetchone()[0])
		cur.execute('SELECT COUNT(*) FROM Restaurants')
		self.assertTrue(0 == cur.fetchone()[0])
		cur.execute('SELECT COUNT(*) FROM Map')
		self.assertTrue(190 == cur.fetchone()[0])
		print('Passed INIT_DB...')

	def test_twitter(self):
		restaurant = FakeRestaurant('K3EBuyhTBTAhR2-ImlrtJg', 'Madras Masala')
		twitter_inst = twitter.Twitter()
		# get tweets fo restaurant
		results = twitter_inst.get_restaurant_tweets(restaurant, reset=True)
		self.assertTrue(len(results) > 0 and len(results) < 50)
		# check if added to DB
		db_results = twitter_inst.check_db(restaurant)
		self.assertTrue(len(db_results) > 0 and len(db_results) < 50)
		# check if same amount of tweets
		self.assertTrue(len(results) == len(db_results))
		# check if in cache
		self.assertTrue(os.path.exists('cache/TWEETS.txt'))
		file_obj = open('cache/TWEETS.txt', 'r')
		file_data = file_obj.read()
		cache = json.loads(file_data)
		file_obj.close()
		self.assertTrue(restaurant.id in cache)
		print('Passed Twitter...')

	def test_restaurants(self):
		yelp_inst = yelp.Yelp()
		# test query
		restaurants, _ = yelp_inst.query('indian', 48104, 10000, 'distance')
		self.assertTrue(len(restaurants) > 0 )
		found = False
		for restaurant in restaurants:
			if restaurant.id == 'K3EBuyhTBTAhR2-ImlrtJg' and restaurant.name == 'Madras Masala':
				found = True
		self.assertTrue(found)
		# test get_restaurant
		restaurant = yelp_inst.get_restaurant('K3EBuyhTBTAhR2-ImlrtJg')
		self.assertTrue(restaurant.rating == 4.0)
		self.assertTrue(restaurant.price == 2)
		self.assertTrue('Indian' in restaurant.categories.split(','))
		# check if in cache
		self.assertTrue(os.path.exists('cache/YELP.txt'))
		file_obj = open('cache/YELP.txt', 'r')
		file_data = file_obj.read()
		cache = json.loads(file_data)
		file_obj.close()
		self.assertTrue(restaurant.id in cache)
		print('Passed Yelp...')

if __name__ == '__main__':
	unittest.main()
	print('All tests passed!')

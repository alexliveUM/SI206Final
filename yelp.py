from requests_oauthlib import OAuth1
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import json
import sys
import sqlite3
import requests
import secrets

class Restaurant:
	def __init__(self, id, name, rating, desc, address, phone, price, hours, url, categories, business_info, similar):
		self.id = id
		self.name = name.replace('"', '')
		self.rating = rating
		self.address = address
		self.phone = phone
		self.categories = categories
		self.url = url
		if isinstance(price, str):
			self.price = len(price)
		else:
			self.price = price
		self.hours = hours
		self.desc = desc.replace('"', '')
		self.business_info = business_info
		self.similar = similar

	# stringify for console output
	def __str__(self):
		return '[{}] {} ({})'.format(self.id, self.name, self.rating)

	# generate string to insert this restaurant into 'Restaurants' in DB
	def insert_str(self):
		return '''
			INSERT INTO "Restaurants" VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")
		'''.format(self.id, self.name, self.rating, self.desc, self.address, self.phone, self.price, self.hours, self.url, self.categories, self.business_info, self.similar)

# Yelp API search instance
class Yelp:
	def __init__(self):
		self.API_KEY = secrets.yelp_api_key
		self.API_HOST = 'https://api.yelp.com'
		self.SEARCH_PATH = '/v3/businesses/search'
		self.BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
		self.conn = sqlite3.connect('SI206DB.db')
		# load categories
		self.categories = {}
		cur = self.conn.cursor()
		cur.execute('SELECT * FROM Map')
		results = cur.fetchall()
		for result in results:
			self.categories[result[1]] = result[2]

	def request(self, host, path, api_key, url_params=None):
		"""Given your API_KEY, send a GET request to the API.
		Args:
			host (str): The domain host of the API.
			path (str): The path of the API after the domain.
			API_KEY (str): Your API Key.
			url_params (dict): An optional set of query parameters in the request.
		Returns:
			dict: The JSON response from the request.
		Raises:
			HTTPError: An error occurs from the HTTP request.
		"""
		url_params = url_params or {}
		url = '{0}{1}'.format(host, quote(path.encode('utf8')))
		headers = {
			'Authorization': 'Bearer %s' % self.API_KEY,
		}

		print(u'Querying {0}...'.format(url))

		response = requests.request('GET', url, headers=headers, params=url_params)
		print(response.json())
		return response.json()

	def search(self, url_params):
		"""Query the Search API by a search term and location.
		Args:
			term (str): The search term passed to the API.
			location (str): The search location passed to the API.
		Returns:
			dict: The JSON response from the request.
		"""
		return self.request(self.API_HOST, self.SEARCH_PATH, self.API_KEY, url_params=url_params)

	# Checks DB for restaurant ID
	# Input: restaurant id (str)
	# Return: DB entry for initializing Restaurant object (tuple)
	def get_restaurant(self, id):
		cur = self.conn.cursor()
		cur.execute('SELECT * FROM Restaurants WHERE Id=?', (id,))
		results = cur.fetchall()
		obj = None
		if len(results):
			rid, rname, rrating, rdesc, raddress, rphone, rprice, rhours, rurl, rcategories, rbusiness_info, rsimilar = results[0]
			obj = Restaurant(rid, rname, rrating, rdesc, raddress, rphone, rprice, rhours, rurl, rcategories, rbusiness_info, rsimilar)			
		return obj

	# Scrapes Yelp page returned from Yelp business object
	# Input: restaurant business from Yelp API (json object)
	# Return: Restaurant object
	def scrape_page(self, r_obj):
		id = r_obj['id']
		name = r_obj.get('name', '')
		print(' >  Scraping page...{}'.format(name))
		url = r_obj.get('url', '')
		address = r_obj['location'].get('display_address', [])
		address = ' '.join(address)
		phone = r_obj.get('display_phone', '')
		price = r_obj.get('price', '')
		rating = r_obj.get('rating', 0.0)
		name = r_obj.get('name', '')
		response = requests.get(url)
		html = response.text
		soup = BeautifulSoup(html, 'html.parser')
		# obtain categories
		categories = ''
		try:
			categories_soup = soup.find('span', class_='category-str-list')
			categories_keys = categories_soup.find_all('a')
			category_list = []
			for category in categories_keys:
				category_list.append(category.text.strip())
			categories = ','.join(category_list)
		except:
			pass
		# obtain hours
		hours = ''
		try:
			days = []
			hours_soup = soup.find('table', class_='table table-simple hours-table')
			days_soup = hours_soup.find_all('tr')
			for el in days_soup:
				first = el.find('th').text.strip()
				second = el.find('td').text.strip()
				days.append('{} = {}'.format(first, second))
			hours = ','.join(days)
		except:
			pass
		# obtain desc
		desc = ''
		try:
			desc_soup = soup.find('div', class_='from-biz-owner-content')
			desc = desc_soup.find('p').text.strip()
		except:
			pass
		# obtain business info
		business_info = ''
		try:
			info_list = []
			ylist = soup.find('div', class_='short-def-list')
			dls = ylist.find_all('dl')
			for dl in dls:
				key = dl.find('dt', class_='attribute-key').text.strip()
				value = dl.find('dd').text.strip()
				info_list.append('{} - {}'.format(key, value))
			business_info = ','.join(info_list)
		except:
			pass
		# related business
		similar = ''
		try:
			similar_list = []
			similar_restaurants = soup.find('div', class_='ywidget related-businesses js-related-businesses')
			similar_keys = similar_restaurants.find_all('div', class_='media-title clearfix')
			for key in similar_keys:
				data = key.find('span')
				similar_list.append(data.text.strip())
			similar = ','.join(similar_list)
		except:
			pass
		return (Restaurant(id, name, rating, desc, address, phone, price, hours, url, categories, business_info, similar), html)

	def query(self, ui_terms='', ui_location=48104, ui_radius=10000, ui_sort='distance'):
		aliases = []
		invalid = []
		# load from cache
		json_obj = {}
		try:
			file_obj = open('cache/YELP.txt', 'r')
			file_data = file_obj.read()
			json_obj = json.loads(file_data)
			file_obj.close()
		except:
			pass
		# process categories
		categories = ui_terms.split()
		print('@@@ Query:', categories)
		# obtain category mapping
		for category in categories:
			if category in self.categories:
				aliases.append(self.categories[category])
			else:
				invalid.append(category)
		# notify user of invalid categories
		if len(invalid):
			print('Following categories in search are invalid. Query constructed withouth these terms:')
			for el in invalid:
				print('\t{}'.format(el))
		# create search query
		url_params = {
			'term':'food', # limited to food options only
			'location': ui_location,
			'radius': ui_radius,
			'categories': ','.join(aliases),
			'limit': 20,
			'sort_by': ui_sort
		}
		# call API
		result = self.search(url_params)
		restaurants = []
		cur = self.conn.cursor()
		for el in result['businesses']:
			print(' - Result', el['id'], el['url'],  el['name'])		
			html = ''
			# check DB
			info = self.get_restaurant(el['id'])
			if info != None:
				print('$$$ Present in DB!')
				restaurants.append(info)
			else:
				print('*** Scraping page!')
				info, html = self.scrape_page(el)
				restaurants.append(info)
				# save to db
				print(info.insert_str())
				cur.execute(info.insert_str())
				self.conn.commit()
			# save to cache
			if info.id not in json_obj and html == '':
				info, html = self.scrape_page(el)
				json_obj[info.id] = {
					'Name': info.id, 
					'Rating': info.rating,
					'Address': info.address,
					'Phone': info.phone,
					'Categories': info.categories,
					'Url': info.url,
					'Price': info.price,
					'Hours': info.hours,
					'Desc': info.desc,
					'BusinessInfo': info.business_info,
					'Similar': info.similar,
					'HTML': html
					}
		# dump to cache 
		with open('cache/YELP.txt', 'w') as outfile:
			json.dump(json_obj, outfile)
		return (restaurants, invalid)

# if __name__ == "__main__":
# 	yelp_obj = Yelp()
# 	query = ''
# 	while True:
# 		query = input('Enter a query: ')
# 		if query.lower() == 'exit':
# 			exit()
# 		result = yelp_obj.query(query.lower())

"""
	Yelp API response format
	{
		region:
		total: // # results
		business: [ // result
				{
					"review_count": 78,
					"distance": 883.5332292665596,
					"id": "6bI31ExV1CGYoy4TGHonnQ",
					"transactions": [
						"restaurant_reservation"
					],
					"location": {
						"display_address": [
							"1220 S University Ave",
							"Ann Arbor, MI 48104"
						],
						"zip_code": "48104",
						"country": "US",
						"address3": "",
						"address1": "1220 S University Ave",
						"city": "Ann Arbor",
						"state": "MI",
						"address2": null
					},
					"image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/htx5ywsBX2DDreN-FapkNA/o.jpg",
					"phone": "+17347477006",
					"is_closed": false,
					"coordinates": {
						"latitude": 42.274783,
						"longitude": -83.7333166
					},
					"display_phone": "(734) 747-7006",
					"categories": [
						{
							"title": "Vietnamese",
							"alias": "vietnamese"
						},
						{
							"title": "Korean",
							"alias": "korean"
						},
						{
							"title": "Chinese",
							"alias": "chinese"
						}
					],
					"price": "$$",
					"name": "One Bowl Asian Cuisine",
					"alias": "one-bowl-asian-cuisine-ann-arbor-4",
					"url": "https://www.yelp.com/biz/one-bowl-asian-cuisine-ann-arbor-4?adjust_creative=d8cdkIwLqRYYmGxRKHTmaQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=d8cdkIwLqRYYmGxRKHTmaQ",
					"rating": 4.0
			},
		]
	}
"""

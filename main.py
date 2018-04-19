from requests_oauthlib import OAuth1
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
from flask import Flask, render_template, request
import twitter
import yelp
import os
import json
import sys
import requests
import secrets
import init_db

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home_route():
	error_msg = []
	if request.method == 'POST':
		yelp_inst = yelp.Yelp()
		ui_categories = ''
		ui_location = ''
		ui_radius = 10000
		ui_sort = 'distance'
		if 'ui_categories' in request.form and request.form['ui_categories'].strip() != '':
			ui_categories = request.form['ui_categories']
		else:
			error_msg.append('Missing required field: Categories')
		if 'ui_location' in request.form and request.form['ui_location'].strip() != '':
			ui_location = request.form['ui_location']
		else:
			error_msg.append('Missing required field: Location')
		if 'ui_radius' in request.form:
			try:
				ui_radius = int(request.form['ui_radius'])
			except:
				error_msg.append('Error in field: Radius. Please enter a valid number between 1000 and 40000.')
		if 'ui_sort' in request.form:
			ui_sort = request.form['ui_sort']
		# if no errors
		if len(error_msg) == 0:
			results, invalid = yelp_inst.query(ui_categories, ui_location, ui_radius, ui_sort)
			return render_template('index.html', error_msg=error_msg, invalid=invalid,restaurants=results)
	# get
	return render_template('index.html', error_msg=error_msg)

@app.route('/restaurant/<r_id>', methods=['GET', 'POST'])
def restaurant_route(r_id):
	yelp_inst = yelp.Yelp()
	twitter_inst = twitter.Twitter()
	tweets = []
	reset = False
	if request.method == 'POST':
		reset = True
	restaurant = yelp_inst.get_restaurant(r_id)
	tweets = twitter_inst.get_restaurant_tweets(restaurant, reset=reset)
	restaurant.price = restaurant.price * '$'
	if restaurant.hours == '':
		restaurant.hours = []
	else:
		restaurant.hours = restaurant.hours.split(',')
	if restaurant.categories == '':
		restaurant.categories = []
	else:
		restaurant.categories = restaurant.categories.split(',')
	if restaurant.business_info == '':
		restaurant.business_info = []
	else:
		restaurant.business_info = restaurant.business_info.split(',')
	if restaurant.similar == '':
		restaurant.similar = []
	else:
		restaurant.similar = restaurant.similar.split(',')
	return render_template('restaurant.html', restaurant=restaurant, tweets=tweets)

@app.route('/categories')
def categories_route():
	categories = []
	yelp_inst = yelp.Yelp()
	categories = yelp_inst.categories
	return render_template('categories.html', categories=categories)

if not os.path.exists('SI206DB.db'):
	init_db.run()
app.run(debug=True)

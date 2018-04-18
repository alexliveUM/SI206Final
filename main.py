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
def default_route():
	if request.method == 'POST':
		return render_template('index.html', request_method='POST')
	else:
		yelp_inst = yelp.Yelp()
		results = yelp_inst.query('')
		print('Default_route:',results)
		for result in results:
			print('\t',result)
		return render_template('index.html', request_method='GET', restaurants=results)

@app.route('/name/<word>')
def name_route(word):
	story_list_json = get_stories('technology')
	headlines = get_headlines(story_list_json)
	return render_template('index.html', name=word, topic='', headlines=[])

@app.route('/headlines/<word>')
def headlines_route(word):
	topic = 'technology'
	story_list_json = get_stories(topic)
	headlines = get_headlines(story_list_json)
	return render_template('index.html', name=word, topic=topic, headlines=headlines[:5])

@app.route('/links/<word>')
def links_route(word):
	topic = 'technology'
	story_list_json = get_stories(topic)
	headlines = get_headlines(story_list_json, True)
	return render_template('index.html', name=word, topic=topic, headlines=headlines[:5])

@app.route('/choose/<word>', methods = ['GET', 'POST'])
def choose_route(word):
	if request.method == 'POST':
		topic = request.form['user_topic']
	else:
		topic = 'technology'
	story_list_json = get_stories(topic)
	headlines = get_headlines(story_list_json, True)
	return render_template('index.html', name=word, topic=topic, choose=True, headlines=headlines[:5])

if not os.path.exists('SI206DB.db'):
	init_db.run()
app.run(debug=True)

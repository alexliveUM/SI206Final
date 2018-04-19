import sqlite3
import json
import csv

def run():
	conn = sqlite3.connect('SI206DB.db')
	cur = conn.cursor()

	# delete
	cur.execute('DROP TABLE IF EXISTS Restaurants; ')
	conn.commit()
	# create
	cur.execute(''' 
		CREATE TABLE 'Restaurants'(
			'Id' TEXT PRIMARY KEY,
			'Name' TEXT,
			'Rating' REAL,
			'Description' TEXT,
			'Address' TEXT,
			'Phone' TEXT,
			'Price' INTEGER,
			'Hours' TEXT,
			'URL' TEXT,
			'Categories' TEXT,
			'BusinessInfo' TEXT,
			'Similar' TEXT
			)
		''')
	conn.commit()

	# delete
	cur.execute('DROP TABLE IF EXISTS Tweets; ')
	conn.commit()
	# create
	cur.execute(''' 
		CREATE TABLE 'Tweets'(
			'Id' TEXT,
			'RestaurantId' TEXT,
			'Username' TEXT,
			'Text' TEXT,
			'Date' TEXT,
			'Retweets' INTEGER,
			'Favorities' INTEGER,
			'Score' INTEGER,
			FOREIGN KEY (RestaurantId) REFERENCES Restaurants(Id)
			)
		''')
	conn.commit()

	# delete
	cur.execute('DROP TABLE IF EXISTS Map; ')
	conn.commit()
	# create
	cur.execute(''' 
		CREATE TABLE 'Map'(
			'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
			'Title' TEXT,
			'Alias' TEXT
			)
		''')
	conn.commit()

	# categories
	try:
		file_obj = open('cache/categories.json', 'r')
		data = json.loads(file_obj.read())
		file_obj.close()
		for datum in data:
			# only track restaurants
			if 'restaurants' in datum['parents']:
				cur.execute('INSERT INTO "Map" VALUES (?, ?, ?)', tuple([None, datum['title'].lower(), datum['alias'].lower()]))
		conn.commit()
	except:
		print('Failed to populate SI206DB with categories.json data. Please verify categories.json exists in cache directory.')	
		conn.close()
		exit(1)

	print('Done!')
	conn.close()


if __name__ == '__main__':
	run()
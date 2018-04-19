Run 'python  main.py' to start the application.

If you would like to reset the application, delete TWEETS.txt and YELP.txt from the cache/ directory, and run 'python init_db.py' to clear and reinitialize the database.

Main.py
	- Python Flask application code
	- Depends on:
		> Twitter.py
		> Yelp.py
		> init_db.py

Twitter.py
	- Contains logic for calling Twitter API
	- Tweet is model that reflects data type in 'Tweets' table
	- Twitter class is object that handles Twitter API calls

Yelp.py
	- Contains logic for calling Yelp Fusion API
	- Restaurant is model that reflects data type in 'Restaurants' table
	- Yelp class is object that handles Yelp Fusion API calls
		- Loads 'categories' from 'Categories' table

init_db.py
	- Contains logic for initializing (and populating) database
	- Creates 'Restaurants', 'Tweets', and 'Map' table
		- 'Restaurant' and 'Tweets' initialized to be empty
		- 'Map' table prepopulated with data from 'categories.json'
			- Category mapping provided from Yelp Fusion API

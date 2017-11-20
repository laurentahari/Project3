## SI 206 2017
## Project 3
## Building on HW7, HW8 (and some previous material!)

##THIS STARTER CODE DOES NOT RUN!!


##OBJECTIVE:
## In this assignment you will be creating database and loading data
## into database.  You will also be performing SQL queries on the data.
## You will be creating a database file: 206_APIsAndDBs.sqlite

import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import sqlite3
import re

## Your name: Lauren Tahari
## The names of anyone you worked with on this project:

#####

##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key #import from twitter_info
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and
# return it in a JSON format
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

## Task 1 - Gathering data

## Define a function called get_user_tweets that gets at least 20 Tweets
## from a specific Twitter user's timeline, and uses caching. The function
## should return a Python object representing the data that was retrieved
## from Twitter. (This may sound familiar...) We have provided a
## CACHE_FNAME variable for you for the cache file name, but you must
## write the rest of the code in this file.

CACHE_FNAME = "206_APIsAndDBs_cache.json"

try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

# Define your function get_user_tweets here:
def get_user_tweets(searchword):
	identity = "twitter_{}".format(searchword) #see if it is in the cache dictionary
	if identity in CACHE_DICTION: #if so, print..
		print ('using cached data')
		twitter_results = CACHE_DICTION[identity] #grab the data from the cache
	else:
		print("api data getting tweets")
		twitter_results = api.user_timeline(searchword) #get it from the internet
		CACHE_DICTION[identity] = twitter_results #add it to dictionary
		##print('getting data from internet for', phrase)

		# get it from the internet
		#twitter_results = public_tweets[]['text']
		# but also, save in the dictionary to cache it! #returns a list # and then write the whole cache dictionary, now with new info added, to the file, so it'll be there even after your program closes!
		cache_file = open(CACHE_FNAME,'w') # open the cache file for writing
		cache_file.write(json.dumps(CACHE_DICTION)) # make the whole dictionary holding data and unique identifiers into a json-formatted string, and write that wholllle string to a file so you'll have it next time!
		cache_file.close()
	return (twitter_results)


def get_user_info(user):
	identity = "user_{}".format(user)  #see if in cache dictionary
	if identity in CACHE_DICTION: #if so.. print
		print ('using cached data user info') #print
		twitter_results = CACHE_DICTION[identity] #grab the data from the cache
	else: #if not using caching
		print("api data getting") #get it from the internet
		twitter_results = api.get_user(user)
		CACHE_DICTION[identity] = twitter_results #add it to dictionary
		##print('getting data from internet for', phrase)

		# get it from the internet
		#twitter_results = public_tweets[]['text']
		# but also, save in the dictionary to cache it! #returns a list # and then write the whole cache dictionary, now with new info added, to the file, so it'll be there even after your program closes!
		cache_file = open(CACHE_FNAME,'w') # open the cache file for writing
		cache_file.write(json.dumps(CACHE_DICTION)) # make the whole dictionary holding data and unique identifiers into a json-formatted string, and write that wholllle string to a file so you'll have it next time!
		cache_file.close()
	return twitter_results

# Write an invocation to the function for the "umich" user timeline and
# save the result in a variable called umich_tweets:
umich_tweets= get_user_tweets('umich') #searching for the "searchword" umich in the tweets

## Task 2 - Creating database and loading data into database
## You should load into the Users table:
# The umich user, and all of the data about users that are mentioned
# in the umich timeline.
# NOTE: For example, if the user with the "TedXUM" screen name is
# mentioned in the umich timeline, that Twitter user's info should be
# in the Users table, etc.

## You should load into the Tweets table:
# Info about all the tweets (at least 20) that you gather from the
# umich timeline.
# NOTE: Be careful that you have the correct user ID reference in
# the user_id column! See below hints.


## HINT: There's a Tweepy method to get user info, so when you have a
## user id or screenname you can find alllll the info you want about
## the user.

## HINT: The users mentioned in each tweet are included in the tweet
## dictionary -- you don't need to do any manipulation of the Tweet
## text to find out which they are! Do some nested data investigation
## on a dictionary that represents 1 tweet to see it!

conn = sqlite3.connect('206_APIsAndDBs.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS Tweets') #make table
cur.execute('DROP TABLE IF EXISTS Users')

table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Users (user_id TEXT PRIMARY KEY, '
table_spec += 'screen_name TEXT, fav_num INTEGER, description TEXT)'
cur.execute(table_spec)

table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Tweets (tweet_id INTEGER PRIMARY KEY, '
table_spec += 'user_id TEXT, time_posted TIMESTAMP, tweet_text TEXT, retweets INTEGER)'
cur.execute(table_spec)

user_info= get_user_info('umich') # load umich user information into  table
user_id= user_info['id_str'] #add these attributes
screen_name=user_info['screen_name']
fav_num= user_info['favourites_count']
description=user_info['description']
what = 'INSERT OR IGNORE INTO Users VALUES (?, ?, ?, ?)'
cur.execute(what, (user_id, screen_name, fav_num, description))

for tweet in umich_tweets:
	for single in tweet['entities']['user_mentions']:
		user_info= get_user_info(single['screen_name'])
		user_id= user_info['id_str']
		screen_name=user_info['screen_name']
		fav_num= user_info['favourites_count']
		description=user_info['description']
		statement = 'INSERT OR IGNORE INTO Users VALUES (?, ?, ?, ?)'
		cur.execute(statement, (user_id, screen_name, fav_num, description))
	statement= 'INSERT INTO Tweets VALUES (?, ?, ?, ?, ?)'
	tweet_id= tweet['id']
	time_posted=tweet['created_at']
	tweet_text=tweet['text']
	retweets= tweet['retweet_count']
	user_id= tweet['user']['id_str']
	cur.execute(statement, (tweet_id, user_id, time_posted, tweet_text, retweets))
conn.commit()

## Task 3 - Making queries, saving data, fetching data

# All of the following sub-tasks require writing SQL statements
# and executing them using Python.

# Make a query to select all of the records in the Users database.
# Save the list of tuples in a variable called users_info.

query = "SELECT * from Users" #select all users
users_info= cur.execute(query).fetchall() #saved into list

# Make a query to select all of the user screen names from the database.
# Save a resulting list of strings (NOT tuples, the strings inside them!)
# in the variable screen_names. HINT: a list comprehension will make
# this easier to complete!
screen_names = [tups[1] for tups in user_info] #use list comprehention to find all screennames; save the list of strings to screen_names

# Make a query to select all of the tweets (full rows of tweet information)
# that have been retweeted more than 10 times. Save the result
# (a list of tuples, or an empty list) in a variable called retweets
query= "SELECT tweet_id, time_posted, tweet_text, user_id, retweets from Tweets WHERE retweets > 10" # select all tweet info and find the tweets that have been retweeted > 10 times
retweets = cur.execute(query).fetchall() #save in list
print (retweets[1][-1]) #identifying retweet count and printing it to pass the test if retweet count >10


#print (retweets)

# Make a query to select all the descriptions (descriptions only) of
# the users who have favorited more than 500 tweets. Access all those
# strings, and save them in a variable called favorites,
# which should ultimately be a list of strings.
query= "SELECT description from Users WHERE fav_num >500" # find where favorite number is more than 500
var = cur.execute(query).fetchall() #save in list
favorites = [tups[0] for tups in var] # using list comprehension and saving to the variable favorites


# Make a query using an INNER JOIN to get a list of tuples with 2
# elements in each tuple: the user screenname and the text of the
# tweet. Save the resulting list of tuples in a variable called joined_data2.


# Make a query using an INNER JOIN to get a list of tuples with 2
# elements in each tuple: the user screenname and the text of the
# tweet in descending order based on retweets. Save the resulting
# list of tuples in a variable called joined_data2.

query= "SELECT Users.screen_name, Tweets.tweet_text from Tweets INNER JOIN Users ON Users.user_id=Tweets.user_id WHERE Tweets.retweets >=1 ORDER BY Tweets.retweets" #order in descending order based on number of retweets
joined_data= cur.execute(query).fetchall() #save in list
joined_data2 = [joined_data] #make it a list

conn.close() #close connection
#print(type(retweets))


### IMPORTANT: MAKE SURE TO CLOSE YOUR DATABASE CONNECTION AT THE END
### OF THE FILE HERE SO YOU DO NOT LOCK YOUR DATABASE (it's fixable,
### but it's a pain). ###

###### TESTS APPEAR BELOW THIS LINE ######
###### Note that the tests are necessary to pass, but not sufficient --
###### must make sure you've followed the instructions accurately!
######
print ("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")


class Task1(unittest.TestCase):
	def test_umich_caching(self):
		fstr = open("206_APIsAndDBs_cache.json","r")
		data = fstr.read()
		fstr.close()
		self.assertTrue("umich" in data)
	def test_get_user_tweets(self):
		res = get_user_tweets("umsi")
		self.assertEqual(type(res),type(["hi",3]))
	def test_umich_tweets(self):
		self.assertEqual(type(umich_tweets),type([]))
	def test_umich_tweets2(self):
		self.assertEqual(type(umich_tweets[18]),type({"hi":3}))
	def test_umich_tweets_function(self):
		self.assertTrue(len(umich_tweets)>=20)

class Task2(unittest.TestCase):
	def test_tweets_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result)>=20, "Testing there are at least 20 records in the Tweets database")
		conn.close()
	def test_tweets_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==5,"Testing that there are 5 columns in the Tweets table")
		conn.close()
	def test_tweets_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT tweet_id FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(result[0][0] != result[19][0], "Testing part of what's expected such that tweets are not being added over and over (tweet id is a primary key properly)...")
		if len(result) > 20:
			self.assertTrue(result[0][0] != result[20][0])
		conn.close()


	def test_users_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=2,"Testing that there are at least 2 distinct users in the Users table")
		conn.close()
	def test_users_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)<20,"Testing that there are fewer than 20 users in the users table -- effectively, that you haven't added duplicate users. If you got hundreds of tweets and are failing this, let's talk. Otherwise, careful that you are ensuring that your user id is a primary key!")
		conn.close()
	def test_users_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==4,"Testing that there are 4 columns in the Users database")
		conn.close()

class Task3(unittest.TestCase):
	def test_users_info(self):
		self.assertEqual(type(users_info),type([]),"testing that users_info contains a list")
	def test_users_info2(self):
		self.assertEqual(type(users_info[0]),type(("hi","bye")),"Testing that an element in the users_info list is a tuple")

	def test_track_names(self):
		self.assertEqual(type(screen_names),type([]),"Testing that screen_names is a list")
	def test_track_names2(self):
		self.assertEqual(type(screen_names[0]),type(""),"Testing that an element in screen_names list is a string")

	def test_more_rts(self):
		if len(retweets) >= 1:
			self.assertTrue(len(retweets[0])==5,"Testing that a tuple in retweets has 5 fields of info (one for each of the columns in the Tweet table)")
	def test_more_rts2(self):
		self.assertEqual(type(retweets),type([]),"Testing that retweets is a list")
	def test_more_rts3(self):
		if len(retweets) >= 1:
			self.assertTrue(retweets[1][-1]>10, "Testing that one of the retweet # values in the tweets is greater than 10")

	def test_descriptions_fxn(self):
		self.assertEqual(type(favorites),type([]),"Testing that favorites is a list")
	def test_descriptions_fxn2(self):
		self.assertEqual(type(favorites[0]),type(""),"Testing that at least one of the elements in the favorites list is a string, not a tuple or anything else")
	def test_joined_result(self):
		self.assertEqual(type(joined_data[0]),type(("hi","bye")),"Testing that an element in joined_result is a tuple")



if __name__ == "__main__":
	unittest.main(verbosity=2)

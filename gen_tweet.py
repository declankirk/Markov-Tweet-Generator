#!/usr/bin/env python
# encoding: utf-8

import sys
import tweepy
import re
import markovify

from config import consumer_key, consumer_secret, access_key, access_secret

# Modified from https://gist.github.com/yanofsky/5436496
def get_all_tweets(screen_name):
	print()
	print("Grabbing tweets from @%s..." % (screen_name))

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

	alltweets = []	
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)
	alltweets.extend(new_tweets)
	oldest = alltweets[-1].id - 1
	
	while len(new_tweets) > 0:
		print("Grabbing tweets before %s..." % (oldest))

		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
		alltweets.extend(new_tweets)
		oldest = alltweets[-1].id - 1
		
		print("%s tweets downloaded so far" % (len(alltweets)))
	
	tweets = ""

	for tweet in alltweets:
		tweetstring = tweet.text
		if tweetstring.startswith("RT"): continue # ignore retweets

		tweetstring = re.sub(r"http\S+", "", tweetstring) # getting rid of links
		tweetstring = re.sub(r"@\S+", "", tweetstring) # so we don't @ people
		tweetstring = re.sub(r".*…", "", tweetstring) # remove quotes of replied tweets

		tweetstring = re.sub(r"&gt;", ">", tweetstring) # encoding...
		tweetstring = re.sub(r"&lt;", "<", tweetstring)
		tweetstring = re.sub(r"&amp;", "&", tweetstring)
		
		tweetstring += '\n'
		tweets += tweetstring
	
	return tweets

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Usage: gen_tweet.py account_name")
		quit()
	
	try:
		tweets = get_all_tweets(sys.argv[1])
	except tweepy.TweepError as e:
		print("TweepError:", e)
		quit()
	
	model = markovify.NewlineText(tweets)
	print()
	print("-------------------------------------------------------")
	print("Hit ENTER to generate another tweet, enter \'q\' to quit.")
	print("-------------------------------------------------------")
	print()
	print(model.make_short_sentence(280, tries=100))
	
	while True:
		arg = input()
		if arg.lower() == "q":
			quit()
		print(model.make_short_sentence(280, tries=100))
import re
import sys
import copy
import tweepy
import urllib.parse
import sys, time, json, requests, uuid

from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler

from dateutil.parser import parse
from datetime import datetime, date, timedelta 

import pandas as pd

def twitter_api_auth(api_key, secret_key, access_token, access_token_secret):

    TWITTER_API_AUTH = {
      'consumer_key': api_key,
      'consumer_secret': secret_key,
      'access_token': access_token,
      'access_token_secret': access_token_secret,
    }

    auth = tweepy.OAuthHandler(api_key, secret_key)
    auth.set_access_token(access_token, access_token_secret)
    auth_api = API(auth, wait_on_rate_limit=True)

    return(auth_api)


def remove_emojis(data):
    emoji = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", re.UNICODE)
    return re.sub(emoji, '', data)


def get_tweets(query, language, num_tweets, auth_api, include_RTs):

    if include_RTs == False:
        query = query + " -filter:retweets"
    print(query)

    all_tweets = []

    for status in Cursor(auth_api.search_tweets, q=query, lang=language, result_type='mixed', tweet_mode = "extended", count=50).items(num_tweets):

        tweet = {}
        tweet_obj = status._json
        
        tweet["source"] = "twitter"
        tweet["query"] = str(query)
        tweet["created_at"] = tweet_obj["created_at"]

        tweet["is_quote_status"] = tweet_obj["is_quote_status"]
        tweet["retweet_count"] = tweet_obj["retweet_count"]
        tweet["favorite_count"] = tweet_obj["favorite_count"]
        tweet["lang"] = tweet_obj["lang"]

        tmp_text = tweet_obj["full_text"].replace('\n','. ').replace('\r','.').replace('..','. ').replace(',.','. ').replace(';.','. ').replace('?.','. ').replace('!.','. ').replace(':.','. ').lstrip('.').lstrip(' ')
        tmp_text = remove_emojis(tmp_text)
        tweet["text"]= tmp_text

        tweet["words"] = len(tweet["text"].split())

        all_tweets.append(tweet)

    all_tweets = pd.DataFrame(all_tweets)
    
    return(all_tweets)



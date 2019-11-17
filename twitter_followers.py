import time
import tweepy
twitter_consumer_key = APPROPRIATE_KEYS
twitter_consumer_secret = APPROPRIATE_KEYS
twitter_access_token = APPROPRIATE_KEYS
twitter_access_secret = APPROPRIATE_KEYS


def get_twitter_followers(screenname):
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_secret)

    api = tweepy.API(auth)

    ids = []
    for page in tweepy.Cursor(api.followers_ids, screen_name=screenname).pages():
        ids.extend(page)

    follower_list = []
    for i in ids:
        u = api.get_user(i)
        follower_list.append(u.name)
        
    return follower_list

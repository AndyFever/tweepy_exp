from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import twitter_credentials
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import json
import geocoder


class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

    def get_trends(self, location):
        g = geocoder.osm(location)
        closest_loc = api.trends_closest(g.lat, g.lng)
        trends = api.trends_place(closest_loc[0]['woeid'])
        return trends

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authentication and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)

    def stream_user_tweets(self, fetched_tweets_filename, user_id):
        # This handles Twitter authentication and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(follow=user_id)


class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            josnObj = json.loads(data)
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write('{}. {}, {}'.format(str(josnObj['id_str']), str(josnObj['created_at']), str(josnObj['text'])))
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['tweet_id'] = np.array([tweet.id for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
        return df


if __name__ == '__main__':

    # Setup the objects needed
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    # Use Case 1: Getting the details of a tweet

    api = twitter_client.get_twitter_client_api()

    # You can see the tweets for the username or the ID
    # tweets = api.user_timeline(screen_name="JoeBiden", count=200)
    # # # Analyse the tweets
    # df = tweet_analyzer.tweets_to_data_frame(tweets)
    # # df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    # print('Last 10 tweets from Joe Biden')
    # print(df.head(10))
    # print('\n Last 10 tweets from Taylor Swift')
    # tweets = api.user_timeline(user_id="17919972")
    # df = tweet_analyzer.tweets_to_data_frame(tweets)
    # print(df.head(10))

    # Use Case 2: Getting the details of the latest trends in a location

    # trends = twitter_client.get_trends('England')
    #
    # for trend in trends[0]['trends']:
    #     print("Name: \t" + str(trend['name']))
    #     print("Tweet Volume: \t" + str(trend['tweet_volume']))
    #     print("Tweet Query: \t" + str(trend['query']))
    #     print('\n')

    # Use Case 4: Streaming tweets of a tag

    # stream = TwitterStreamer()
    # stream.stream_tweets("test.json", ['#PMQs'])
    #

    # Use Case 5: Streaming a collection of tweets from people
    stream = TwitterStreamer()
    stream.stream_user_tweets('user_tweets.json', ['27646232', '23009949', '3257608936', '20536157'])


    # twitter_client = TwitterClient()
    # tweet_analyzer = TweetAnalyzer()

    # api = twitter_client.get_twitter_client_api()
    #
    # tweets = api.user_timeline(screen_name="JoeBiden", count=200)
    #
    # # This uses the user_timeline API which brings back tweets for a user ID
    # tweets = api.user_timeline(user_id="27646232")
    #
    # # Analyse the tweets
    # df = tweet_analyzer.tweets_to_data_frame(tweets)
    # df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    #
    # print(df.head(10))

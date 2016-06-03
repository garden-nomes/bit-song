import time
import json
import tweepy
import os


access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']


class NoTweetsYet(Exception):
    pass


class TweetFeeder(tweepy.StreamListener):

    def __init__(self):
        # call StreamListener init
        super(TweetFeeder, self).__init__()

        # set up local data
        self.last_status = None

        # handle auth
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # start listener
        self.stream = tweepy.Stream(auth, self)
        self.stream.sample(async = True)

    def on_status(self, status):
        self.last_status = status
        return True

    def on_error(self, status):
        print(status)
        return False

    def get_tweet(self):
        '''Grab a random status
        '''
        if self.last_status == None:
            raise NoTweetsYet
        return self.last_status

    def disconnect(self):
        self.stream.disconnect()

    def ready(self):
        return self.last_status != None


if __name__ == '__main__':
    listener = TweetFeeder()
    while True:
        try:
            time.sleep(1)
            print(listener.get_tweet())
        except NoTweetsYet:
            pass
        except KeyboardInterrupt:
            listener.disconnect()
            print
            exit()

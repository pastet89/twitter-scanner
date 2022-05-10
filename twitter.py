import json  
import requests as r
from time import sleep
from tenacity import retry, stop_after_attempt, wait_fixed
from helpers import email_notification
from config import (
    TWITTER_BEARER_TOKEN, SECONDS_BETWEEN_REQUEST,
    MAX_RESULTS, MINUTES_TO_CHECK_FEEDS, TWITTER_ID,
)
from copy import copy


tracked_users = {
        "NFTLandAlpha":  {"keyword_filter": None},
        "Imaginary_Ones":  {"keyword_filter": "WL|REVEAL|Reveal|reveal|Discord"},
}


################################################################################
# DO NOT EDIT BELOW THIS LINE!
################################################################################


class TwitterDataTracker(object):
    def __init__(self):
        self.set_db_from_file()

    def set_db_from_file(self):
        with open('db.json', "r") as json_file:
            self.db = json.loads(json_file.read())
    
    def set_emailed_tweet(self, tweet_id):
        if tweet_id not in self.db:
                self.db[tweet_id] = {}
        self.db[tweet_id]["emailed"] = True
        self.store_db_to_file()

    def store_db_to_file(self):
        with open('db.json', 'w') as json_file:
            json_file.write(json.dumps(self.db))

    def is_emailed(self, tweet_id):
        try:
            return self.db[tweet_id]["emailed"]
        except KeyError:
            return False


class TwitterCore(object):
    base_url = "https://api.twitter.com/2"
    base_url_v1 = "https://api.twitter.com/1.1"
    token = TWITTER_BEARER_TOKEN
    twitter_id = TWITTER_ID
    sign_headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

    def __init__ (self, tracked_users):
        self.set_users(tracked_users)
        self.users_to_last_tweets = {
            tu: 1 for tu in tracked_users
        }
        self.data_tracker = TwitterDataTracker()

    def is_successfull(self, response):
        return response.status_code in (200, 201)

    def set_users(self, tracked_users):
        self.tracked_users = tracked_users
        for user in self.tracked_users.copy().keys():
            self.tracked_users[user]["id"] = self.user_to_user_id(user)
            sleep(1)

    @retry(stop=stop_after_attempt(1802), wait=wait_fixed(2))
    def get_signed_request(self, url):
        response = r.get(url, headers=self.sign_headers)
        if self.is_successfull(response):
            return json.loads(response.text)
        raise Exception(response.text)


class TwitterBot(TwitterCore):
    def get_user_id_by_user(self, user):
        url = f"{self.base_url}/users/by/username/{user}"
        return self.get_signed_request(url)

    def user_to_user_id(self, user):
        return self.get_user_id_by_user(user)["data"]["id"]

    def get_filters_from_user(self, user):
        return self.tracked_users[user]["keyword_filter"]

    def get_max_tweets(self, since_id):
        if since_id == 1:
            return 10
        return MAX_RESULTS

    def get_timeline_by_user(self, user, user_id):
        since_id = self.users_to_last_tweets[user]
        max_tweets = self.get_max_tweets(since_id)
        url = (
            f"{self.base_url}/users/{user_id}/tweets?"
            f"since_id={since_id}&exclude=replies&max_results={max_tweets}"
        )
        return self.get_signed_request(url)

    def process_user(self, user, user_data):
        user_id = user_data["id"]
        api_data = self.get_timeline_by_user(user, user_id)
        try:
            res_count = api_data["meta"]["result_count"]
        except KeyError:
            if api_data["errors"]["type"] == "https://api.twitter.com/2/problems/resource-not-found":
                return
        if res_count < 1:
            return
        tweets = api_data["data"]
        last_tweet = tweets[0]
        last_tweet_id = last_tweet["id"]
        last_stored_tweet_id = self.users_to_last_tweets[user]
        if last_stored_tweet_id != last_tweet_id:
            self.users_to_last_tweets[user] = last_tweet_id
            for tweet in tweets[::-1]:
                self.process_tweet(user, user_data, tweet)

    def passes_filter(self, filters, text):
        words = filters.split("|")
        for word in words:
            if word in text:
                return True

    def process_tweet(self, user, user_data, tweet):
        filters = self.get_filters_from_user(user)
        if not filters or self.passes_filter(filters, tweet["text"]):
            self.send_tweet(user, tweet)

    def send_tweet(self, user, tweet):
        link = f"https://twitter.com/{user}/status/{tweet['id']}"
        text = tweet["text"] + "<br />" + link
        if not self.data_tracker.is_emailed(tweet['id']):
            self.data_tracker.set_emailed_tweet(tweet["id"])
            email_notification(f"New tweet from {user}", text)

    def process_tweets(self):
        while True:
            for user, user_data in self.tracked_users.items():
                self.process_user(user, user_data)
                sleep(SECONDS_BETWEEN_REQUEST)
            sleep(60 * MINUTES_TO_CHECK_FEEDS)


def main():
    tp = TwitterBot(tracked_users)
    tp.process_tweets()
    

if __name__ == "__main__":
    try:
        main()
    finally:
        email_notification(
            "Twitter bot crashed",
            """Something happened, restart the bot! Most likely this is because some
            of the tracked twitter accounts changed its name or was deleted.
            To find the exact error, run the bot manyally with `python twitter.py`"""
        )
    

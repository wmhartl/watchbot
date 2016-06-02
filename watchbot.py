import tweepy
import glob
import random
import os
from datetime import datetime, date, time

consumer_key = "REDACTED"
consumer_secret_key = "REDACTED"
access_token = "REDACTED"
access_token_secret = "REDACTED"

def tweet_update(status):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    if not status:
        print "Tweet error"
    else:
        api.update_status(status)

def setup_google_search(lead_string, site_string):
    dt = datetime.now()
    outstring = lead_string + "+" + dt.strftime("%B+%d+%Y") + "+site:" + site_string
    return outstring.lower()

#start
#Changes directory to where the script is located (easier cron scheduling, allows you to work with relative paths)
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

print setup_google_search("wruw","watchuseek.com")

tweet_update("Hello world, this is watchesbot!")
tweet_update("")

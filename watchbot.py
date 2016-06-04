import tweepy
from bs4 import BeautifulSoup
import glob
import random
import urllib2
import string
import re
import os
from datetime import datetime, timedelta, date, time
from watchconfig import *  # import config

def tweet_update(status):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    if not status:
        print "Tweet error"
    else:
        api.update_status(status)

def google_search_url(lead_string, site_string):
    dt = datetime.now() - timedelta(days=days_to_subtract)
    searchstring = lead_string + "+" + dt.strftime("%-d+%B+%Y") + "+site:" + site_string  # %-d may not work on Windows
    search_url=google_image_search_url
    search_url=string.replace(search_url,"##",searchstring, 1)
    return search_url.lower()

def exec_google_search(url):
    print url
    header = {'User-Agent': user_agent}
    htmlresp = BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)))
    #images = [a['data-src'] for a in htmlresp.find_all("img", {"data-src": re.compile("gstatic.com")})]
    images = htmlresp.find_all("script")
    for each in images:
        print each

# main
# Changes directory to where the script is located (easier cron scheduling, allows you to work with relative paths)
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

print exec_google_search(google_search_url(search_text, search_site))
#tweet_update("Hello world, this is watchesbot!")
#tweet_update("")

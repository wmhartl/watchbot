import tweepy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date, time
import hashlib
import os
import re
import string
import urllib2
import sqlite3
from watchconfig import *  # import config

def tweet_update(status, filename=None):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    if not status and not filename:
        print "Tweet error"
    else:
        if filename:
            api.update_with_media(filename, status)
        else:
            api.update_status(status)

def google_search_url(lead_string, site_string):
    dt = datetime.now() - timedelta(days=days_to_subtract)
    searchstring = lead_string + "+" + dt.strftime("%-d+%B+%Y") + "+site:" + site_string  # %-d may not work on Windows
    search_url=google_image_search_url
    search_url=string.replace(search_url,"##",searchstring, 1)
    return search_url.lower()

def exec_google_search(url):
    #print url
    header = {'User-Agent': user_agent}
    htmlresp = BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)))
    imagesresp = [a['href'] for a in htmlresp.find_all("a", {"href": re.compile("jpg")})]
    return imagesresp

def parse_images(images):
    possible_images = []
    for each in images:
        try:
            output = each.split('=')[1]
            output = output.split('&')[0]
            possible_images.append(output)
        except:
            output = None

    return possible_images

def capture_image(url):
    raw_img = urllib2.urlopen(url).read()
    filename = hashlib.sha256(raw_img).hexdigest() + ".jpg"
    f = open(filename, 'wb')
    f.write(raw_img)
    f.close()
    return filename

# main
# Changes directory to where the script is located (easier cron scheduling, allows you to work with relative paths)
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

conn = sqlite3.connect(database_file)
db = conn.cursor()
if os.path.getsize(database_file)<100:
    db.execute("create table images(filename text, url text, date text)")

images = exec_google_search(google_search_url(search_text, search_site))
image_urls = parse_images(images)
print image_urls

#TODO: adjust code to find one a pic not used in image_urls
db.execute("select rowid from images where url = ?", (image_urls[0], ))
rowid = db.fetchall()
if len(rowid)==0:
    print "not found"
else:
    print "found"
image_url = image_urls[0]
print image_url

image_file = capture_image(image_url)
print image_file
print datetime.now()

db.execute("insert into images values (?, ?, ?)", (image_file, image_url, datetime.now()))
conn.commit()
conn.close()

#tweet_update("", image_file)

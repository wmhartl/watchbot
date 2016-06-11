# watchbot.py

import tweepy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import cookielib
import hashlib
import logging
import os
import re
import string
import urllib2
import sqlite3
from watchconfig import *  # import config

# prevent automatic redirection
class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response

# post actual tweets - can post just text or text and media
def tweet_update(status, filename=None):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    if not status and not filename:
        logging.error("Nothing to tweet")
    else:
        if filename:
            api.update_with_media(filename, status)
        else:
            api.update_status(status)

# create the google search url used for the image search
def google_search_url(lead_string, site_string):
    dt = datetime.now() - timedelta(days=days_to_subtract)
    try:
        searchstring = lead_string + "+" + dt.strftime("%-d+%B+%Y") + "+site:" + site_string  # %-d may not work on Win
    except:
        searchstring = lead_string + "+" + dt.strftime("%d+%B+%Y") + "+site:" + site_string
    search_url=google_image_search_url
    search_url=string.replace(search_url,"##",searchstring, 1)
    return search_url.lower()

# execute the google search and do a basic link parse looking for hrefs to jpgs
def exec_google_search(url):
    logging.debug(url)
    header = {'User-Agent': user_agent}
    try:
        htmlresp = BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)))
    except:
        logging.error("Initial Google search failed")
        htmlresp = ""
    imagesresp = [a['href'] for a in htmlresp.find_all("a", {"href": re.compile("jpg")})]
    return imagesresp

# so we can exclude image sites that act difficultly
def safe_site(teststring):
    for each in excluded_sites:
        if each in teststring:
            logging.debug("Excluded site: " + teststring)
            return False
    return True

# parse out a list of possible images for downloading
def parse_images(images):
    possible_images = []
    for each in images:
        try:
            output = each.split('=')[1]
            output = output.split('&')[0]
            if safe_site(output):
                possible_images.append(output)
        except:
            logging.error("Split error")
    return possible_images

# walk the possible images checking each in the DB by URL to find one that isn't already downloaded
def find_unused_image(image_urls, conn):
    db = conn.cursor()
    image_url = None
    for each in image_urls:
        logging.debug(each + "?")
        db.execute("select rowid from images where url = ?", (each,))
        rowid = db.fetchall()
        if len(rowid) == 0:
            image_url = each
            break
    return image_url

# grab the image - handling redirection, then ensure we have a place to put the image, SHA256 hash the image
#    to get a unique filename, and store it on disk
def capture_image_to_file(url):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
    try:
        response = opener.open(url)
    except:
        return None
    if response.code != 200:
        if response.code == 302 or response.code == 301:
            url = response.headers['Location']
            logging.debug("Redirected to " + url)
        else:
            logging.error("error fetching image")
            logging.error(response.code)
            logging.error(response.headers)
            return None
    try:
        raw_img = urllib2.urlopen(url).read()
    except:
        raw_img = ""
    d = os.path.dirname(image_path)
    if not os.path.exists(d):
        try:
            os.makedirs(image_path)
        except:
            logging.error("cannot create path")
    filename = image_path + hashlib.sha256(raw_img).hexdigest() + ".jpg"
    f = open(filename, 'wb')
    f.write(raw_img)
    f.close()
    return filename

# --- main ---
# change to location so it's easier to get to db from within cron
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# open our database, and if it's uninitialized, set it up
conn = sqlite3.connect(database_file)
db = conn.cursor()
if os.path.getsize(database_file)<100:
    db.execute("create table images(filename text, url text, date text)")

# find a unique unused image for posting
images = exec_google_search(google_search_url(search_text, search_site))
image_urls = parse_images(images)
logging.debug(image_urls)
image_url = find_unused_image(image_urls, conn)
logging.debug(image_url)

# if we found an image, store it in the DB and tweet it; if not, end on an error
if image_url:
    image_file = capture_image_to_file(image_url)
    logging.debug(image_file)
    logging.debug(datetime.now())

    db.execute("insert into images values (?, ?, ?)", (image_file, image_url, datetime.now()))
    conn.commit()
    conn.close()
    tweet_update(tweet_message, image_file)
else:
    conn.close()
    logging.error("Could not find a unique image")
    exit(-1)

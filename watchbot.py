import tweepy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date, time
import cookielib
import hashlib
import logging
import os
import re
import string
import urllib2
import sqlite3
from watchconfig import *  # import config

class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response

def tweet_update(status, filename=None):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    if not status and not filename:
        logging.error("Tweet error")
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
    logging.debug(url)
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
            if "photobucket" not in output:
                possible_images.append(output)
        except:
            logging.error("Split error")

    return possible_images

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

def capture_image_to_file(url):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
    response = opener.open(url) #, urlencode(data))
    if response.code != 200:
        if response.code == 302 or response.code == 301:
            url = response.headers['Location']
            logging.debug("Redirected to " + url)
        else:
            logging.error("error fetching")
            logging.error(response.code)
            logging.error(response.headers)
            return None

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
logging.debug(image_urls)

image_url = find_unused_image(image_urls, conn)
logging.debug(image_url)

if image_url:
    image_file = capture_image_to_file(image_url)
    logging.debug(image_file)
    logging.debug(datetime.now())

    db.execute("insert into images values (?, ?, ?)", (image_file, image_url, datetime.now()))
    conn.commit()
    #tweet_update("", image_file)
else:
    logging.error("Could not find a unique image")

conn.close()

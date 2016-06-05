# watchconfig.py

# Twitter API key configuration from https://apps.twitter.com/
consumer_key = "REDACTED"
consumer_secret_key = "REDACTED"
access_token = "REDACTED"
access_token_secret = "REDACTED"

# image storage
image_path = "REDACTED"

# Google search configuration
google_image_search_url = "https://www.google.com/search?q=##&source=lnms&tbm=isch"   # using ## for string replace
search_site = "watchuseek.com"  # search a specific site
search_text = "wruw"  # search string
days_to_subtract = 2  # to search historically rather than on the current date

# exclude these image sites
excluded_sites = ["photobucket.com"]

# database config
database_file = "watches.db"

# URL request config
user_agent = "Mozilla/5.0 (X11; Linux armv7l; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.8.0"

# tweet messages to include with images - if removed initialize as tweet_message = ""
tweet_message = "#watches"

from datetime import datetime, timedelta
import random
import tweepy
import spacy
import json

from spacy.en import English

from short_unicode import EMOJI_UNICODE

from secret import *

global nlp

INPUT_FILE = 'aphorisms.txt'
VAL_THRESHOLD = .6

DATE_FORMAT = '%Y-%m-%d'
START_DATE = '2016-02-16'
TWEETS_FILE = 'tweets.json'
GENERATE_TWEETS = False  # Generate the tweets or just post them?

start_date = datetime.strptime(START_DATE, DATE_FORMAT)

def init_emoji():
    emoji_doc = {}
    for k in EMOJI_UNICODE:
        emoji_doc[k] = {}
        doc = nlp(k)
        emoji_doc[k]['value'] = EMOJI_UNICODE[k]
        emoji_doc[k]['doc'] = doc[0]
    return emoji_doc
    
def find_closest(w, emoji_doc):
    """Find the closest match between two words by vector similarity"""
    closest = None
    closest_val = 0
    for k in emoji_doc:
        de = emoji_doc[k]['doc']
        if w.similarity(de) > closest_val:
            closest_val = w.similarity(de)
            closest = k

    if closest:
        return emoji_doc[closest], closest_val

def _auth():
    """Authorize the service with Twitter"""
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

def post_tweet(tweet):
    # print("Posting message {}".format(tweet))
    api = _auth()
    api.update_status(tweet, lat=41.9000, long=12.5000)

def process_source(line, emoji_doc):
    tweet = None
    doc = nlp(line)
    emojis = []
    for token in doc:
        if token.pos == spacy.parts_of_speech.NOUN or token.pos == spacy.parts_of_speech.VERB or token.pos == spacy.parts_of_speech.ADJ:
            res = find_closest(token, emoji_doc)
            if res:
                closest, closest_val = res
                if closest_val > VAL_THRESHOLD:
                    if closest['value'] not in emojis:
                        emojis.append(closest['value'])
    if len(emojis) != 0:
        tweet = line + ' '.join(emojis)
    return tweet
   
if __name__ == '__main__':


    if GENERATE_TWEETS:
        nlp = English()    
        out = []        
        emoji = init_emoji()
        source = [x.strip() for x in open(INPUT_FILE)]
        for i, line in enumerate(source):
            day = start_date + timedelta(days=i)
            tweet = process_source(line, emoji)
            if tweet:

                out.append((day.strftime('%Y-%m-%d'), tweet))
        json.dump(out, open(TWEETS_FILE, 'w'))                
    else:
        today = datetime.now().date()
        source = json.load(open(TWEETS_FILE, 'r'))
        for line in source:
            date, tweet = line
            if today == datetime.strptime(date, DATE_FORMAT).date():
                post_tweet(tweet)

import random
import tweepy
from spacy.en import English

from short_unicode import EMOJI_UNICODE

from secret import *

nlp = English()    
    
INPUT_FILE = 'aphorisms.txt'
VAL_THRESHOLD = .6

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
#        print(w, w.pos_, de)
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
    print("Posting message {}".format(tweet))
    api = _auth()
    api.update(status=tweet)

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
                        #print(token, closest['value'], closest, closest_val,)
    if len(emojis) != 0:
        tweet = line + ' '.join(emojis)
    return tweet
   
if __name__ == '__main__':
    emoji = init_emoji()
    source = [x.strip() for x in open(INPUT_FILE)]
    line = random.choice(source)
    tweet = process_source(line, emoji)
    if tweet:
        #post_tweet(tweet)
        print(tweet)

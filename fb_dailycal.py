from flask import Flask
from flask.ext.script import Manager
from datetime import datetime, timedelta, timezone
import mandrill
import requests
import json
import os

app = Flask(__name__)
manager = Manager(app)

'''Send request to graph API to get the messages, likes counts, and created times
for the UC Berkeley Free and For Sale page (FB ID: 266259930135554)'''
r = requests.get('https://graph.facebook.com/266259930135554/feed?access_token=' + os.environ['ACCESS_TOKEN'] + '&fields=message,likes.limit(500),created_time')
json_data = r.json()['data']

# list of words to check for in Facebook posts
word_list = ["gun", "knife", "chase", "homeless", "follow", "followed", "grope", "groped", "shoot", "PSA", "steal"]

@manager.command
def index():
    for i in range(0,len(json_data)):
        # get time string provided in Facebook json
        date_time = json_data[i]['created_time'].split("T")
        # turn time string into datetime
        p_time = datetime.strptime(date_time[0] + date_time[1][:-5], "%Y-%m-%d%H:%M:%S")
        # check if the time of post + 1 hour is less than the current time
        if datetime.now().utcnow() <= p_time + timedelta(hours = 1):
            # get Facebook post text
            fb_text = json_data[i]['message']
            r = requests.get('http://text-processing.com/api/sentiment/')
            payload = { 'text' : fb_text }
            res = requests.post('http://text-processing.com/api/sentiment/', data=payload)
            get_sentiment = json.loads(res.text)['probability'] # turn into JSON and get probability
            # check if negative sentiment is greater than 0.5
            if get_sentiment['neg'] >= 0.5:
                # check if any word in word_list is in the Facebook post text
                for word in word_list:
                    if word in fb_text:
                        # if one of the words is in the post, then send an email
                        mandrill_client = mandrill.Mandrill(os.environ['MANDRILL_KEY'])
                        message = {'text': fb_text,
                            'from_email': os.environ['FROM_EMAIL'],
                            'from_name': 'Daily Cal Alert',
                            'subject': 'Daily Cal Alert',
                            'to': [{'email': os.environ['TO_EMAIL'],
                                 'name': 'Daily Cal',
                                 'type': 'to'}]}
                        result = mandrill_client.messages.send(message=message)

if __name__ == "__main__":
    manager.run()

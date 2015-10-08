from flask import Flask
from flask.ext.script import Manager
from datetime import datetime, timedelta, timezone
import mandrill
import requests
import os

app = Flask(__name__)
manager = Manager(app)

r = requests.get('https://graph.facebook.com/266259930135554/feed?access_token=' + ACCESS_TOKEN + '&fields=message,likes.limit(500),created_time')
json_data = r.json()['data']
word_list = "arson assault blackmail burglary fraud hijacking kidnapping mugging mugger murderer robber shoplifter smuggler terrorist thief vandal appeal barrister caution cell community service court court case death penalty defense fine jail guilty imprisonment innocent judge jury justice lawyer offence sentence prison probation prosecution punishment corporal punishment remand home solicitor trial verdict witness arrest ban break burgle charge escape investigate rob steal armed burglar alarm illegal weapon gun knife incident accident homeless"

@manager.command
def index():
    for i in range(1,len(json_data)):
        date_time = json_data[i]['created_time'].split("T")
        p_time = datetime.strptime(date_time[0] + date_time[1][:-5], "%Y-%m-%d%H:%M:%S")
        fb_text = json_data[i]['message']
        if datetime.now().utcnow() <= p_time + timedelta(hours = 1):
            if any(word in fb_text for word in word_list.split()):
                mandrill_client = mandrill.Mandrill(MANDRILL_KEY)
                message = {'text': fb_text,
                    'from_email': FROM_EMAIL,
                    'from_name': 'Daily Cal Alert',
                    'subject': 'Daily Cal Alert',
                    'to': [{'email': TO_EMAIL,
                         'name': 'Daily Cal',
                         'type': 'to'}]}
                result = mandrill_client.messages.send(message=message)

if __name__ == "__main__":
    manager.run()

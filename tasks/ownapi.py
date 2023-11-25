# This is a solution to ownapi task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# Some additional dependencies necessary:
# - pip install flask
# - you need to have SSL cert (or not?) see ssl_context=('cert.pem', 'key.pem') passed to Flask
#
#
# The overall goal is to:
# 1. run Flask, which will open port 2137
# 2. send the URL of my own hosted api to aidevs
# 3. wait for answers
# 4. Profit!

import requests
import json
import yaml
import os
from flask import Flask, request

def load_apikey():
    """Loads the aidevs API key from ~/.aidevs2"""
    with open(os.path.expanduser('~/.aidevs2'), 'r') as file:
        api_key = yaml.safe_load(file)
    return api_key['APIKEY']

def load_openai_key():
    """Loads the openai API key from ~/.aidevs2"""
    with open(os.path.expanduser('~/.aidevs2'), 'r') as file:
        api_key = yaml.safe_load(file)
    return api_key['OPENAI_KEY']

BASE_URL = 'https://zadania.aidevs.pl'
APIKEY = load_apikey()
OPENAI_KEY = load_openai_key()
TASK = 'knowledge'

from flask import Flask
app = Flask(__name__)

@app.route("/v1/knowledge", methods=['POST'])
def hello():
    return {
        "answer": "yes"
    }

if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'), port=2137)

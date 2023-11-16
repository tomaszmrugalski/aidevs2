# This is a solution to the embedding task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs -
# 3. ...
# 4. ...
# 5. ...
# 6. Send the answer to aidevs

import requests
import json
import yaml
import os.path
import sys

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
TASK = 'embedding'

# STEP 1: Get the token from aidevs
url = BASE_URL + '/token/' + TASK
print(f'aidevs: Getting {url}, sending {APIKEY}')
page = requests.post(url, json={ "apikey": APIKEY })
data = json.loads(page.text)
token = data['token']
print(f"aidevs: My token is {token}")

# STEP 2: Get the task: ...
url = BASE_URL + '/task/' + token

query={  }
print(f"aidevs: Sending {query} to {url}")
page2 = requests.post(url, data=query)
data2 = json.loads(page2.text)

print(f"aidevs: the task is {data2}")

# STEP 3: SOLUTION: Use text-embedding-ada-002 to generate text embedding for the question "Hawaiian pizza"
# Non-GPT solution. Find word that starts with capital letter.
input = 'Hawaiian pizza'

url = 'https://api.openai.com/v1/embeddings'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "input": input, "model": "text-embedding-ada-002"}
print(f'OpenAI, step 1: Getting {url}, using {OPENAI_KEY}')
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"OpenAI, step 1: Response body: {data}")

embeddings = data['data'][0]['embedding']

print(f"Embeddings: {len(embeddings)} element(s)")

# STEP 6: Send the answer
url = BASE_URL + '/answer/' + token
answer={ 'answer': embeddings }
print(f'aidevs: Getting {url}, sending {answer}')
page3 = requests.post(url, json = answer)
data3 = json.loads(page3.text)
print(f"aidevs: /answer/token returned {data3}")

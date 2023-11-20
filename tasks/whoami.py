# This is a solution to the whoami task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs
# 3. ...
# 4. Send the answer to aidevs
# 5. Profit!

import requests
import json
import yaml
import os.path
import os
import sys
from time import sleep

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
TASK = 'whoami'

# STEP 1: Get the token from aidevs
url = BASE_URL + '/token/' + TASK
print(f'aidevs: Getting {url}, sending {APIKEY}')
response1 = requests.post(url, json={ "apikey": APIKEY })
data = json.loads(response1.text)
token = data['token']
print(f"aidevs: My token is {token}")

# STEP 2: Get the task from aidevs

system_prompt = 'Twoim zdaniem jest odganięcie osoby, o której mowa. Użytkownik będzie podawał kolejne podpowiedzi. Jeżeli nie wiesz, o jaką osobę chodzi, to powiedz nie wiem. Jeżeli jesteś pewien, powiedz tylko imię i nazwisko, nic więcej.'


attempt = 1

hints = []

while attempt < 10:
    url = BASE_URL + '/task/' + token
    query={  }
    print(f"aidevs: Sending {query} to {url}")
    response2 = requests.post(url, data=query)
    data2 = json.loads(response2.text)
    hint = data2['hint']
    if hint not in hints:
        hints.append(hint)
    else:
        print("aidevs: Hint already provided, sleeping for 5 seconds, retrying")
        sleep(5)
        continue
    print(f"aidevs: the hint {attempt} is {hint}")

    lmbd = lambda x: { 'role': 'user', 'content': x }


    url = 'https://api.openai.com/v1/chat/completions'
    headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
    body = { "messages": [{ "role": "system", "content": system_prompt}] + list(map(lmbd, hints)), "model": "gpt-3.5-turbo"}

    print(f"Iteration {attempt}, sending {body}")

    attempt = attempt + 1


    print(f'OpenAI, attempt {attempt}: Getting {url}, using {OPENAI_KEY}')
    page = requests.post(url, json=body, headers=headers)
    data = json.loads(page.text)
    print(f"OpenAI, step 1: Response body: {data}")
    answer = data['choices'][0]['message']['content']
    print(f"OpenAI answer: the answer is {answer}")

    if answer.lower().find("nie wiem") == -1:
        # STEP 4: Send the answer
        url = BASE_URL + '/answer/' + token
        print(f'aidevs: Getting {url}, sending {answer}')
        response3 = requests.post(url, json = { "answer": answer })
        data3 = json.loads(response3.text)
        print(f"aidevs: /answer/token returned {data3}")

        sys.exit(0)

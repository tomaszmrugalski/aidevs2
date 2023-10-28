# Basic script that connects to openAPI

import requests
import json
import yaml
import os.path

def load_apikey():
    with open(os.path.expanduser('~/.aidevs2'), 'r') as file:
        api_key = yaml.safe_load(file)
    return api_key['OPENAI_KEY']

APIKEY = load_apikey()



url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {APIKEY}' }
body = { "messages": [{ "role": "user", "content": "Hello!" }], "model": "gpt-3.5-turbo"}

print(f'Getting {url}, using {APIKEY}')
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"Response body: {data}")
print(f"Response headers: {page.headers}")

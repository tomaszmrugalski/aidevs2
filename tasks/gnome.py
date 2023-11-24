# This is a solution to the gnome task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# Bibliography: https://platform.openai.com/docs/guides/vision
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs - URL to an image
# 3. Send the image to GPT-4-vision and ask to determine the color of the hat, return it in polish.
# 4. Send the answer to aidevs
# 5. Profit!

import requests
import json
import yaml
import os

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
TASK = 'gnome'

# STEP 1: Get the token from aidevs
url = BASE_URL + '/token/' + TASK
print(f'aidevs: Getting {url}, sending {APIKEY}')
response1 = requests.post(url, json={ "apikey": APIKEY })
resp = json.loads(response1.text)
token = resp['token']
print(f"aidevs: My token is {token}")

# STEP 2: Get the task from aidevs
url = BASE_URL + '/task/' + token
query={  }
print(f"aidevs: Sending {query} to {url}")
response2 = requests.post(url, data=query)
data2 = json.loads(response2.text)
print(f"aidevs: response: {data2}")
image_url = data2['url']


# STEP 3: Send the image to GPT-4-vision-preview
url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }

system_prompt = 'Your task is to determine if there is a gnome in the image user uploads.' +\
                'If there is respond briefly with the color of the hat IN POLISH. If there is no gnome, say ERROR.'
messages=[
    {
        "role": "system",
        "content": system_prompt
    },
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": image_url,
          },
        },
      ],
    }
  ]

body = { "messages": messages, "model": "gpt-4-vision-preview"}

print(f'OpenAI: Getting {url}, using {OPENAI_KEY}')
print(f"OpenAI: system prompt: {system_prompt}")
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
print(f"OpenAI answer: the response is {data}")
answer = data['choices'][0]['message']['content']
print(f"OpenAI answer: the answer is {answer}")

# STEP 4: Send the answer to aidevs
url = BASE_URL + '/answer/' + token
print(f'aidevs: Getting {url}, sending {answer}')
response3 = requests.post(url, json = { "answer": answer })
data3 = json.loads(response3.text)
print(f"aidevs: /answer/token returned {data3}")

# STEP 5: Profit!

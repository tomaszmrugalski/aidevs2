# This is a solution to the knowledge task from aidevs2 course
# See https://zadania.aidevs.pl/ for details
#
# The overall goal is to:
# 1. Get a token from aidevs
# 2. Get the task from aidevs - the two links to knowledge materials, also the question to be answered.
# 3. Get the first knowledge source - current exchange rates for currencies
# 4. Get the second knowledge source - population info for all countries
# 5. Use both sources in system prompt and send the question to GPT
# 6. Send the answer to aidevs
# 7. Profit!

import requests
import json
import yaml
import os
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
TASK = 'knowledge'

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
question = data2['question']
print(f"aidevs: response: {data2}")
print(f"aidevs: the question is: {question}")


#STEP 3: Get the currency exchange report.
rates = requests.get(url="http://api.nbp.pl/api/exchangerates/tables/A/?format=json")
rates = json.loads(rates.text)[0]['rates']
rates_txt = ''
for c in rates:
    rates_txt = rates_txt + f"{c['currency']}/{c['code']} {c['mid']}, "

# STEP 4: Get the population info.
countries = requests.get(url="https://restcountries.com/v3.1/all?fields=name,population")
countries = json.loads(countries.text)

print(f"retrieved info about {len(countries)} countries.")
population = ""
for c in countries:
    population = population + (f"{c['name']['common']} - {c['population']} people, ")


# STEP 5: Assemble a prompt, ask GPT to answer question.

system_prompt = 'Odpowiedz krótko na pytanie używając Twojej wiedzy i informacji poniżej. ' + \
                '%% Aktualne kursy walut: ' + rates_txt + \
                '%% Populacja krajów: ' + population

url = 'https://api.openai.com/v1/chat/completions'
headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENAI_KEY}' }
body = { "messages": [{ "role": "system", "content": system_prompt}, {"role":"user", "content": question}], "model": "gpt-3.5-turbo"}

print(f'OpenAI: Getting {url}, using {OPENAI_KEY}')
print(f"OpenAI: system prompt: {system_prompt}")
print(f"OpenAI: user message: {question}")
page = requests.post(url, json=body, headers=headers)
data = json.loads(page.text)
answer = data['choices'][0]['message']['content']
print(f"OpenAI answer: the answer is {answer}")

# STEP 6: Send the answer to aidevs
url = BASE_URL + '/answer/' + token
print(f'aidevs: Getting {url}, sending {answer}')
response3 = requests.post(url, json = { "answer": answer })
data3 = json.loads(response3.text)
print(f"aidevs: /answer/token returned {data3}")

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

import json
import yaml
import os
import requests
from flask import Flask, request, jsonify

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

HOST = '::'
PORT = 2137

memories = []

from flask import Flask
app = Flask(__name__)

@app.route('/')
def root():
    return 'Hello, aidevs!'

@app.route("/v1/knowledge", methods=['POST'])
def hello():
    content = request.json
    print(f"Received {content} from {request.remote_addr}")

    system_prompt = 'Odpowiedz krótko na pytania usera.'
    if len(memories) > 0:
        system_prompt = system_prompt + '\n' 'User poprzednio dostarczył nastepujacych informacji:\n' + '\n'.join(memories)
    question = content['question']

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

    if '?' not in question:
        print("This looks like a statement, I'll remember it.")
        memories.append(question)

    return jsonify({
        "reply": answer
    })

if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'), host=HOST, port=PORT)

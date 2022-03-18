from flask import Flask, request
import requests
import config
import os
import json
from flask_caching import Cache

app = Flask(__name__)
options = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 30000000,
    "SECRET_KEY": 'node-key',
    "ENV": 'development'
}
app.config.from_mapping(options)
cache = Cache(app)

def return_committed(key):
    requests.get('http://127.0.0.1:5000/committed?key=' + key)

def send_message(type, key, extra=""):
    '''Send messages to all replicas. Type can be one of PREPREPARE, PREPARE, COMMIT'''
    port = str(request.server[1])
    for i in range(config.NUMBER_OF_NODES):
        requests.get('http://127.0.0.1:500' + str(i+1) + '/' + type.lower() + '?port='+ port +'&key=' + key + extra)

@app.route('/')
def index():
    '''Index page route'''

    return '<h1>Application Deployed!</h1>'

@app.route('/init', methods=['GET'])
def init_request():
    '''Primary receives a request from client'''

    args = request.args
    if "key" not in args:
        return 'Argument Error'
    # assigns the request a sequence number and broadcasts to all replicas
    sequence_number = 1
    send_message("PREPREPARE", args["key"], "&b=" + str(sequence_number))
    print('Primary sent preprepare messages')
    return "Primary sent preprepare messages"

@app.route('/preprepare', methods=['GET'])
def preprepare():
    args = request.args
    if "key" not in args:
        return 'Argument Error'
    if "b" not in args:
        return 'Argument Error'
    key = args["key"]

    if not cache.get("b") or int(args["b"]) > int(cache.get("b")):
        cache.set("b", int(args["b"]))
        send_message("PREPARE", key)
    print("Preprepare received by port " + str(request.server[1]))
    return "Preprepare"

@app.route('/prepare', methods=['GET'])
def prepare():
    args = request.args
    if "key" not in args:
        return 'Argument Error'
    key = args["key"]

    if not cache.get("prepare_messages"):
        messages = {}
    else:
        messages = cache.get("prepare_messages")
    messages[key] = messages.get(key, 0) + 1
    if messages[key] >= config.NUMBER_OF_F*2 + 1:
        send_message("COMMIT", key)
        # reset messages for this key so we don't send it again
        del messages[key]
    cache.set("prepare_messages", messages)
    print("Prepare received by " + str(request.server[1]) + " sent by " + args["port"])
    return "Prepare"

@app.route('/commit', methods=['GET'])
def commit():
    args = request.args
    if "key" not in args:
        return 'Argument Error'
    key = args["key"]
    if not cache.get("commit_messages"):
        messages = {}
    else:
        messages = cache.get("commit_messages")
    messages[key] = messages.get(key, 0) + 1
    port = request.server[1]
    if messages[key] >= config.NUMBER_OF_F*2 + 1:
        # return committed message to service
        return_committed(key)
        # reset messages for this key so we don't send it again
        del messages[key]
    cache.set("commit_messages", messages)
    print("Commit received by " + str(request.server[1]) + " sent by " + args["port"])
    return "Commit"

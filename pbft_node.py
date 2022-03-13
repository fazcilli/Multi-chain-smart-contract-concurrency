from flask import Flask, session, request
import requests
import config
import os
import json
app = Flask(__name__)
app.config.update(SECRET_KEY='node-key', ENV='development')

def send_message(type, key, extra=""):
    '''Send messages to all replicas. Type can be one of PREPREPARE, PREPARE, COMMIT'''
    for i in range(config.NUMBER_OF_NODES):
        requests.get('http://127.0.0.1:500' + str(i+1) + '/' + type.lower() + '?key=' + key + extra)

def send_request(key, port):
    '''Upon successfull pbft consensus, send request to all copies of the smart contract'''
    from web3 import Web3, HTTPProvider

    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(config.BLOCKCHAIN_ADDRESS))
    # Set the default account (so we don't need to set the "from" for every transaction call)
    web3.eth.defaultAccount = web3.eth.accounts[0]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(current_dir + config.CONTRACT_PATH) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    # Fetch deployed contract references
    contract = web3.eth.contract(address=config.CONTRACT_ADDR, abi=contract_abi)

    # Call contract function (this is not persisted to the blockchain)
    contract.functions.setGreetings(key).call()
    print("Set greetings called from port " + str(port))

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

    if "b" not in session:
        session["b"] = args["b"]
        send_message("PREPARE", key)
    elif args["b"] > session["b"]:
        session["b"] = args["b"]
        send_message("PREPARE", key)
    print("Preprepare received by " + request.url)
    return "Preprepare"

@app.route('/prepare', methods=['GET'])
def prepare():
    args = request.args
    if "key" not in args:
        return 'Argument Error'
    key = args["key"]

    if "prepare_messages" not in session:
        session["prepare_messages"] = {}
    messages = session["prepare_messages"]
    messages[key] = messages.get(key, 0) + 1
    session["prepare_messages"] = messages
    if messages[key] >= config.NUMBER_OF_F*2 + 1:
        send_message("COMMIT", key)
    print("Prepare received by " + request.url + " sent by " + request.remote_addr)
    return "Prepare"

@app.route('/commit', methods=['GET'])
def commit():
    args = request.args
    if "key" not in args:
        return 'Argument Error'
    key = args["key"]

    if "commit_messages" not in session:
        session["commit_messages"] = {}
    messages = session["commit_messages"]
    messages[key] = messages.get(key, 0) + 1
    session["commit_messages"] = messages
    port = request.url
    if messages[key] >= config.NUMBER_OF_F*2 + 1:
        # send request to smart contract
        send_request(key, port)
    print("Commit received by " + request.url + " sent by " + request.remote_addr)
    return "Commit"

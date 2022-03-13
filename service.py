import json
import os
import random
import config
import requests
from flask import Flask, session

service = Flask(__name__)
service.config.update(SECRET_KEY='service-key', ENV='development')

@service.route('/')
def index():
    '''Index page route'''
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
    message = contract.functions.getGreetings().call()

    text = "<h1>PBFT service!</h1><br/><br/><br/>"
    text += "<p>Current message from smart contract: "+message+"</p><br/><br/><br/>"
    return text + '<h2>To simulate smart contract update go to <a href="http://127.0.0.1:5000/simulate">http://127.0.0.1:5000/simulate</a></h2>'

@service.route('/simulate')
def simulate():
    '''Simulates a pbft consensus. If the consensus approves the request, a message will be sent to all copies of the smart contract'''
    session["primary"] = random.randint(1, config.NUMBER_OF_NODES)
    request = json.dumps({"newkey": "newvalue"})
    # send initial request to primary
    requests.get('http://127.0.0.1:500' + str(session["primary"]) + '/init' + '?key=' + request)
    return "<h2>Return <a href='/'>Home</a> to see if message has changed</h2>"

def clean():
    for i in range(config.NUMBER_OF_NODES):
        os.system("kill -9 $(lsof -ti:{})".format(str(5001 + i)))
    os.system("kill -9 $(lsof -ti:5000)")

def register_pbft_nodes():
    command = "export FLASK_APP=pbft_node;"
    for i in range(config.NUMBER_OF_NODES):
        command += "export FLASK_RUN_PORT=" + str(5001 + i) + ";"
        command += "flask run"
        command += " & "
    command += "export FLASK_APP=service; export FLASK_RUN_PORT=5000; flask run"
    os.system(command)


if __name__ == '__main__':
    clean()
    register_pbft_nodes()

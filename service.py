import json
import random
import config
import requests
import time
from flask import Flask, request
from flask_caching import Cache
import utils
from solcx import install_solc
install_solc(version='latest')

service = Flask(__name__)
options = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 30000000,
    "SECRET_KEY": 'service-key',
    "ENV": 'development'
}
service.config.from_mapping(options)
cache = Cache(service)
from web3 import Web3, HTTPProvider

# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(config.BLOCKCHAIN_ADDRESS))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]

@service.route('/')
def index():
    '''Index page route'''

    contracts = cache.get("contracts") or []
    text = "<h1>Offchain service!</h1><br/><br/><br/>"
    text += str(config.NUMBER_OF_NODES) + " offchain nodes active. </br>"
    text += str(len(contracts)) + " smart contracts found. </br><ul>"
    for c in contracts:
        contract = web3.eth.contract(**c)
        message = contract.functions.greet().call()
        text += "<li><b>Address:</b> " + c["address"] + " , <b>Message:</b> " + message + "</li>"
    text += "</ul>"
    text += '<h2>To create smart contracts go to <a href="http://127.0.0.1:5000/create?number=2">http://127.0.0.1:5000/create?number=2</a></h2>'
    text += '<h2>To simulate smart contract update go to <a href="http://127.0.0.1:5000/simulate">http://127.0.0.1:5000/simulate</a></h2>'

    text += '<h2>To evaluate with the current configuration in config.py go to <a href="http://127.0.0.1:5000/evaluate">http://127.0.0.1:5000/evaluate</a></h2>'
    return text

@service.route('/simulate')
def simulate():
    '''Simulates a pbft consensus. If the consensus approves the request, a message will be sent to all copies of the smart contract'''
    start = time.time()
    cache.set("primary", random.randint(1, config.NUMBER_OF_NODES))
    key = json.dumps({"newkey": "newvalue"})
    primary = str(cache.get("primary"))
    # send initial request to primary
    requests.get('http://127.0.0.1:500' + primary + '/init' + '?key=' + key)
    messages = cache.get("committed_messages") or {}

    while time.time() - start < config.TIMEOUT_SECONDS:
        time.sleep(1)
        if key in messages and messages[key] >= config.NUMBER_OF_F + 1:
            print("f+1 committed message received by offchain nodes. Updating contracts...")
            updateSmartContracts()
            end = time.time()
            # reset messages for this key so we don't send it again
            del messages[key]
            n = len(cache.get("contracts") or [])
            f = config.NUMBER_OF_F
            text = "<h2>Successfully committed.</h2><br/><h2>Return <a href='/'>Home</a> to see if message has changed</h2>"
            text += "<br/>" + "Operation took %.2gs" % (end - start)
            text += "<br>N: " + str(n)
            text += "<br>F: " + str(f)
            return text
    return "Timeout."

@service.route('/committed')
def committed():
    args = request.args
    if "key" not in args:
        return 'Argument Error'
    key = args["key"]
    if not cache.get("committed_messages"):
        messages = {}
    else:
        messages = cache.get("committed_messages")

    messages[key] = messages.get(key, 0) + 1
    cache.set("committed_messages", messages)
    return "Success. Return <a href='/'>Home</a> to see if smart contracts are updated."

def updateSmartContracts():
    contracts = cache.get("contracts") or []
    for c in contracts:
        contract = web3.eth.contract(**c)
        tx_hash = contract.functions.setGreeting('New message').transact()
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

@service.route('/create')
def createsmartcontracts():

    args = request.args
    try:
        number = int(args["number"])
    except:
        number = 2

    utils.create_contracts(number, cache)
    contracts = cache.get("contracts") or []
    text = str(len(contracts)) + " Contracts created. </br><ul>"
    for c in contracts:
        contract = web3.eth.contract(**c)
        message = contract.functions.greet().call()
        text += "<li><b>Address:</b> " + c["address"] + " , <b>Message:</b> " + message + "</li>"
    return text + "</ul><br/>Return <a href='/'>home</a>"

@service.route('/evaluate')
def evaluate():
    cache.set("contracts", [])
    utils.create_contracts(config.NUMBER_OF_CONTRACTS, cache)
    text = simulate()
    return text

def tp_storage_update():
    tps_opts = cache.get('tps')
    tpb_opts = cache.get('tpb')
    contract_storage = web3.eth.contract(**tps_opts)
    contract_backup = web3.eth.contract(**tpb_opts)
    hash = contract_storage.functions.proposeValue("key1", 3).transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)

    hash = contract_backup.functions.proposeValue("key1", 3).transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)

    hash = contract_storage.functions.store("key1", 3).transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)

    hash = contract_backup.functions.store("key1", 3).transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)

    last_entry = contract_storage.functions.getLastEntry().call()
    print("Key: " + last_entry[0] + ", Value: " + str(last_entry[1]))
    return "Key: " + last_entry[0] + ", Value: " + str(last_entry[1])

@service.route('/tps')
def tp_storage():
    tps_opts = utils.create_tpstorage()
    tpb_opts = utils.create_tpbackup()

    contract_storage = web3.eth.contract(**tps_opts)
    contract_backup = web3.eth.contract(**tpb_opts)
    # set backup
    hash = contract_storage.functions.setBackupAddr(tpb_opts["address"]).transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)
    # set backup
    hash = contract_backup.functions.setBackupAddr(tps_opts["address"]).transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)

    cache.set("tps", tps_opts)
    cache.set("tpb", tpb_opts)

    start = time.time()
    cache.set("primary", random.randint(1, config.NUMBER_OF_NODES))
    key = json.dumps({"newkey": "newvalue"})
    primary = str(cache.get("primary"))
    # send initial request to primary
    requests.get('http://127.0.0.1:500' + primary + '/init' + '?key=' + key)
    messages = cache.get("committed_messages") or {}
    text = ""
    while time.time() - start < config.TIMEOUT_SECONDS:
        time.sleep(1)
        if key in messages and messages[key] >= config.NUMBER_OF_F + 1:
            print("f+1 committed message received by offchain nodes. Updating contracts...")
            tp_storage_update()
            end = time.time()
            # reset messages for this key so we don't send it again
            del messages[key]
            n = len(cache.get("contracts") or [])
            f = config.NUMBER_OF_F
            text = "<h2>Successfully committed.</h2><br/>"
            text += "<br/>" + "Operation took %.2gs" % (end - start)
            text += "<br>N: 2"
            text += "<br>F: " + str(f)
            break

    text += "<br/><br/>Key value pair added to smart contracts: <br/>"
    last_entry = contract_storage.functions.getLastEntry().call()
    print("Key: " + last_entry[0] + ", Value: " + str(last_entry[1]))
    text += "<br>Key: " + last_entry[0] + ", Value: " + str(last_entry[1])
    return text


if __name__ == '__main__':
    utils.clean()
    utils.register_pbft_nodes()

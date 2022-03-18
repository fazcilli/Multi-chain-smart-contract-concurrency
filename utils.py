import os

from web3 import Web3, HTTPProvider

# Client instance to interact with the blockchain
import config

web3 = Web3(HTTPProvider(config.BLOCKCHAIN_ADDRESS))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]


def create_contracts(number, cache):
    from solcx import compile_source
    compiled_sol = compile_source(
        '''
            pragma solidity >0.5.0;

             contract Greeter {
                 string public greeting;
        
                 constructor() public {
                     greeting = 'Hello';
                 }
        
                 function setGreeting(string memory _greeting) public {
                     greeting = _greeting;
                 }
        
                 function greet() view public returns (string memory) {
                     return greeting;
                 }
             }
         ''',
        output_values=['abi', 'bin']
    )
    contract_id, contract_interface = compiled_sol.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    Hello = web3.eth.contract(abi=abi, bytecode=bytecode)
    # create n copies of smart contract
    for i in range(number):
        hash = Hello.constructor().transact()
        receipt = web3.eth.wait_for_transaction_receipt(hash)
        contracts = cache.get("contracts") or []
        contracts.append({"address": receipt.contractAddress,"abi": abi})
        cache.set("contracts", contracts)

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

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

def create_tpbackup():
    from solcx import compile_source
    compiled = compile_source('''
        pragma solidity >=0.7.0 <0.9.0;

        interface IStorage{
            function getQueueLastEntry() external view returns (string memory, uint);
        }
        
        // Sample struct to store basic key-value pair
        struct info_piece { string key; uint value ;}
        
        contract TPSbackup {
            address private TPSDuplicate;
        
            info_piece[] _storage;
            info_piece[] _queue;
            string temp;
            string backup_temp;
                    
            constructor() public {
                info_piece memory inf = info_piece("default1", 1);
                 _storage.push(inf);
             }
        
            function setBackupAddr(address ad) public{
                TPSDuplicate = ad;
            }
        
            function proposeValue(string memory k, uint val) public{
                EnqueueValue(k, val);
            }
        
            
            function EnqueueValue(string memory k, uint val) private{
                info_piece memory inf = info_piece(k, val);
                _queue.push(inf);
            }
        
            function DequeueValue() private view returns (string memory, uint){
                uint len = _queue.length;
                if (len == 0) {
                    return ("", 0);
                }
                info_piece memory inf = _queue[len-1];
                return (inf.key, inf.value);
            }
        
            function store(string memory k, uint val) public{
                temp = k;
                info_piece memory inf = info_piece(k, val);
                if (crossCheckCommitValue()){
                    _storage.push(inf);
                }
            }
        
            function getQueueLastEntry() public view returns (string memory, uint){
                return DequeueValue();
            }
        
            function crossCheckCommitValue() private returns (bool){
                uint val1; uint val2;
                (temp, val1) = DequeueValue();
                (backup_temp, val2) = getBackupQueueEntry();
                if ((keccak256(abi.encodePacked(temp)) == keccak256(abi.encodePacked(backup_temp))) && (val1 == val2)){
                     return true;
                } else {
                    revert("Different values sent to different contracts. Transaction cannot be validaed. ");
                }
            }
        
            function getLastStoredEntry() public view returns (string memory, uint){
                uint len = _storage.length;
                if (len == 0) {
                    return ("", 0);
                }
                return (_storage[len-1].key, _storage[len-1].value);
            }
        
            function getBackupQueueEntry() private view returns (string memory, uint){
                return IStorage(TPSDuplicate).getQueueLastEntry();
            }
        }
        ''', output_values=['abi', 'bin'])
    contract_id, contract_interface = compiled.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    Hello = web3.eth.contract(abi=abi, bytecode=bytecode)
    hash = Hello.constructor().transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)
    opts = {"address": receipt.contractAddress,"abi": abi}
    return opts

def create_tpstorage():
    from solcx import compile_source
    compiled = compile_source('''
        pragma solidity >=0.7.0 <0.9.0;
    
        // Sample struct to store basic key-value pair
        struct info_piece { string key; uint value ;}
        
        interface IBackup{
            function getQueueLastEntry() external view returns (string memory, uint);
        }
        
        contract TPStorage {
        
            address private TPSDuplicate;
            info_piece[] _storage;
            info_piece[] _queue;
            string temp;
            string backup_temp;
            
            constructor() public {
                info_piece memory inf = info_piece("default1", 1);
                 _storage.push(inf);
             }
        
            function setBackupAddr(address ad) public{
                TPSDuplicate = ad;
            }
        
            function proposeValue(string memory k, uint val) public{
                EnqueueValue(k, val);
            }
        
            function getLastEntry() public view returns (string memory, uint){
                uint len = _storage.length;
                if (len == 0) {
                    return ("", 0);
                }
                return (_storage[len-1].key, _storage[len-1].value);
            }
        
            function EnqueueValue(string memory k, uint val) private{
                info_piece memory inf = info_piece(k, val);
                _queue.push(inf);
            }
        
            function DequeueValue() private view returns (string memory, uint){
                uint len = _queue.length;
                if (len == 0) {
                    return ("", 0);
                }
                info_piece memory inf = _queue[len-1];
                return (inf.key, inf.value);
            }
        
            function store(string memory k, uint val) public{
                temp = k;
                info_piece memory inf = info_piece(k, val);
                _storage.push(inf);
            }
        
            function crossCheckCommitValue() private returns (bool){
                uint val1; uint val2;
                (temp, val1) = DequeueValue();
                (backup_temp, val2) = getBackupQueueEntry();
                if ((keccak256(abi.encodePacked(temp)) == keccak256(abi.encodePacked(backup_temp))) && (val1 == val2)){
                     return true;
                } else {
                    revert("Different values sent to different contracts. Transaction cannot be validaed. ");
                }
            }
        
            function getQueueLastEntry() public view returns (string memory, uint){
                return DequeueValue();
            }
        
            function getBackupQueueEntry() private view returns (string memory, uint){
                return IBackup(TPSDuplicate).getQueueLastEntry();
            }
        }
        ''', output_values=['abi', 'bin'])
    contract_id, contract_interface = compiled.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    Hello = web3.eth.contract(abi=abi, bytecode=bytecode)
    hash = Hello.constructor().transact()
    receipt = web3.eth.wait_for_transaction_receipt(hash)
    opts = {"address": receipt.contractAddress,"abi": abi}
    return opts



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

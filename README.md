
<div id="top"></div>

# Multichain Transaction Systems

<!-- GETTING STARTED -->
## Getting Started

In order to run our prototype, first we will install a local Ethereum network and deploy a smart contract. Then using the offchain cluster, we will be updating the smart contract concurrently.

### Prerequisites
* Install node and npm
* Install geth
  ```sh
  $ brew tap ethereum/ethereum
  $ brew install ethereum
  ```
* Install truffle
  ```sh
  $ npm install -g truffle
  ```
* Install solidity
  ```sh
  $ npm install -g solc
  ```
* Install python packages
  ```sh
  $ pip install requirements.txt
  ```

### Network Setup

1. Initialize blockchain
    ```sh
    $ geth --datadir blkchain init genesis.json
    ```
2. Bring up the Private Ethereum blockchain
   ```sh
   $ geth --port 3000 --networkid 58343 --nodiscover --datadir=./blkchain --maxpeers=0 --http.port 8543 --http.addr 127.0.0.1 --http.corsdomain "*" --http.api "eth,net,web3,personal,miner" --allow-insecure-unlock --http
   ```
3. Connect to the private Ethereum blockchain using the Geth Javascript console
   ```sh
   $ geth attach http://127.0.0.1:8543
   ```
4. Create an account and “mine” for dummy Ether. Make a note of the account identifier. And start mining.
   ```sh
   > personal.newAccount('seed')
   > personal.unlockAccount(web3.eth.coinbase, "seed", 15000)
   > miner.start()
   ```
5. Initialize truffle
   ```sh
   $ cd truffle
   $ truffle init
   ```
6. Update the value of `from` inside `truffle_config.js` to the account identifier assigned after `personal.newAccount('seed')` command.
7. Compile and deploy the smart contract. Make a note of the contract address after successful migration.
   ```sh
   $ truffle compile
   $ truffle migrate
   ```
8. Update config.py `CONTRACT_ADDR` with the output of migrate command


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Run service.py, which will create a service on http://127.0.0.1:5000 with by default 4 offchain nodes on ports 5001, 5002, 5003, 5004. Go to http://127.0.0.1:5000 to see the current message in the smart contract.
   ```sh
   $ python service.py
   ```


In order to simulate a transaction, go to http://127.0.0.1:5000/simulate



<p align="right">(<a href="#top">back to top</a>)</p>


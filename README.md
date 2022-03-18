
<div id="top"></div>

# Multichain Transaction Systems

<!-- GETTING STARTED -->
## Getting Started

In order to run our prototype, first we will install a local Ethereum network and install the libraries required to run the service. 

### Prerequisites
* Install node and npm
* Install geth
  ```sh
  $ brew tap ethereum/ethereum
  $ brew install ethereum
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
4. Create an account and “mine” for dummy Ether. And start mining.
   ```sh
   > personal.newAccount('seed')
   > personal.unlockAccount(web3.eth.coinbase, "seed", 15000)
   > miner.start()
   ```


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

- Run service.py, which will create a service on http://127.0.0.1:5000 with by default 4 offchain nodes on ports 5001, 5002, 5003, 5004. Go to http://127.0.0.1:5000 to interact with the service.
   ```sh
   $ python service.py
   ```
- In order to create copies of our template smart contract, go to http://127.0.0.1:5000/create?number=x (x=number of smart contracts, default=2)

- In order to simulate a transaction, go to http://127.0.0.1:5000/simulate



<p align="right">(<a href="#top">back to top</a>)</p>


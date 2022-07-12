
from unittest.mock import Mock
from brownie import (interface, network, config, accounts, MockV3Aggregator, VRFCoordinatorMock, LinkToken, Contract)
from web3 import Web3

##mainly 3 diffnt ways to get account=
#1.accounts[0] 
#2.accounts.add(env)
#3.accounts.load(id)

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}

decimals = 8
startingprice = 20000000000000
FORKED_BLOCKCHAINS = ['mainnet-fork','mainnet-fork-dev']
LOCAL_BLOCKCHAIN_NETWORKS = ['development','ganache-local']
def get_account(index = None,id = None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
        ##the above 2 are used if specifications...
        ##the brownie accounts generate 'id' is not working
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS or network.show_active() in FORKED_BLOCKCHAINS:
        ##in forked blockchain, we spin up our local ganache instance so as to get the accounts...
        return accounts[0]
    else:
        ##config file is an environment variable file, hence all vars inside of it, are considered as env vars
        return accounts.add(config["wallets"]["from_key"])

##used to deploy the mock contracts if the environment is a local one/development one, or the ganache-local

def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.
        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        ##hence it becomes a must to deploy the mocks
        if len(contract_type) <= 0:
            ##when we understand the first contract type itself is not there, then we deploy all of the types, and 
            ## and in the succeeding function calls, it goes by/gets address using contract_type[-1]
            # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi
    return contract

DECIMALS = 8
INITIAL_VALUE = 200000000000
##2000 followed by 8 decimals

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    ##the thing is that all 3 are being deloyed together, within a single fn
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")

def checklength():
    account = get_account()
    return ([len(MockV3Aggregator),len(LinkToken),len(VRFCoordinatorMock)])

def fund_with_link(to_address, account = None, link_token = None, amount = 100000000000000000):
    #0.1 LINK
    if account:
        pass
    else:
        account = get_account()
    
    if link_token:
        link_token = link_token
    else:
        link_token = get_contract('link_token')
    
    tx = link_token.transfer(to_address,amount,{'from':account})
    #linktokencontract = interface.LinkTokenInterface(link_token.address)
    #linktokencontract.transfer(to_address,amount,{'from':account})
    tx.wait(1)
    print('link has been funded')
    return tx
    
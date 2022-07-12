from brownie import accounts, network, Lottery, config
from web3 import Web3
import time
from scripts.helpful_scripts import (
    get_account, 
    deploy_mocks, 
    get_contract, 
    checklength,
    fund_with_link)

def deploylottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("abc", False),
    )
    
    print("Deployed lottery!")
    print(checklength())
    return Lottery[-1]

def startlottery():
    account = get_account()
    lotterycurrent = Lottery[-1]
    tx = lotterycurrent.start_lottery({'from':account})
    tx.wait(1)
    ##assuming lottery already exists
    ##must do the tx.wait(1), since asynchronous, brownie gets confused
    print('you have started the lottery')

def enter_lottery(player_address):
    account = get_account()
    lotterythis = Lottery[-1]
    ##be sure to add 1-2 Wei so as to be completely sure, --- to consult a sr solidity developer abt this
    #10^9 wei is a gwei
    val = lotterythis.getEntranceFee()
    tx = lotterythis.enter({
        'from':player_address,
        'value':val+1000000000
    })
    tx.wait(1)
    print('you have entered the lottery!')

def endlottery():
    account = get_account()
    lottery = Lottery[-1]
    #to fund the contract so as to use the randomness function
    tx=fund_with_link(lottery.address)
    tx.wait(1)
    endingtransaction = lottery.end_lottery()
    endingtransaction.wait(1)
    ##now it is the chainlink node`s turn to respond to the callback function, rawrandomness wala fn...
    ##hence we need to wait for it before we close the script, hence why we do the following:
    time.sleep(60)
    print(f"{lottery.recentWinner} is the winner of this lottery")
    ##but we dont have a chainlink node in our ganache instance, hence whywe wont get any winner
    #now we will learn on how to get around that in our testing study for this project

def main():
    deploylottery()
    startlottery()
    enter_lottery(get_account())
    endlottery()

    ##integration tests vs unit tests

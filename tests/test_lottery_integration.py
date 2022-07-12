##we are gonna do an integration test on a live chain - i.e. rinkeby, and then proceed to deploy it onto rinkeby itself
## we will be writing only one test

from brownie import network
from scripts.helpful_scripts import get_account, fund_with_link, LOCAL_BLOCKCHAIN_NETWORKS
from scripts.deloylottery import deploylottery
import pytest
from web3 import Web3
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    else:
        lottery = deploylottery()
        account = get_account()
        lottery.start_lottery({'from':account})
        lottery.enter({
            'from':account,
            'value':lottery.getEntranceFee()
        })
        lottery.enter({
            'from':account,
            'value':lottery.getEntranceFee()
        })
        fund_with_link(lottery)
        lottery.end_lottery({
            'from':account
        })
        time.sleep(60)
        ##basically it will be doing ntg for a minute, in hopes that the chainlink node will respond by then
        i = 0
        while(lottery.recentWinner() == '0x0000000000000000000000000000000000000000'):
            i+=1
        
        print(i)
        assert lottery.recentWinner() == account
        ##since only account is taking part in the lottery, both the times, hecne winner = account
        #assert lottery.balance == 0
        ##the above line is giving assertion error now...
        ##patrick added the bracket after balance, later on.. to try that
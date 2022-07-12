from brownie import accounts,Lottery,config, network, exceptions
#from scripts.deloylottery import deploylottery
from web3 import Web3
import pytest
from scripts.deloylottery import deploylottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_NETWORKS, fund_with_link, get_account, get_contract
##so in unit tests we are testing each and every line of code
def test_get_entrance_fee():
#    account = accounts[0]
#    lottery_this = Lottery.deploy(config['networks'][network.show_active()]['ethusdt-pricefeed'],{'from':account})
#    getEntr = lottery_this.getEntranceFee()
#    #print(getEntr)
#    assert (lottery_this.getEntranceFee()) >= Web3.toWei(0.023,"ether")
#    assert (lottery_this.getEntranceFee()) <= Web3.toWei(0.027,"ether")
###mainnet forking?
##the above thing is what was written before

    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    else:
        ###ARRANGE
        lottery = deploylottery()
        ###ACT
        entrance_fee_actual = lottery.getEntranceFee()
        entrance_fee_expected = Web3.toWei(0.025,"ether")
        ###ASSERT
        assert entrance_fee_actual == entrance_fee_expected
    
def test_cant_enter_if_lotterynotstarted():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    else:
        lottery = deploylottery()
        with pytest.raises(exceptions.VirtualMachineError):
            lottery.enter({'from':get_account(),'value':lottery.getEntranceFee()})

def test_can_enter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    else:
        lottery = deploylottery()
        lottery.start_lottery({'from':get_account()})
        lottery.enter({'from':get_account(), 'value': lottery.getEntranceFee()})
        ##do note we are freely asserting that the get_account will be the account that deployed the contract, since it is a local blockchain, and 
        ##get_account will take the very first account... on every get_account call
        assert lottery.players_read()[0] == get_account()

def test_can_endlottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    else:
    #Arrange
        lottery = deploylottery()
        lottery.start_lottery({'from':get_account()})
        lottery.enter({'from':get_account(), 'value': lottery.getEntranceFee()})
        ##lottery has been entered
    #Act
        fund_with_link(lottery)
        lottery.end_lottery({'from':get_account()})
        print(f'the current lottery state is {lottery.lottery_state_read()}')
        assert lottery.lottery_state_read() == 2

def test_can_pickwinner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    else:
    #Arrange
        lottery = deploylottery()
        lottery.start_lottery({'from':get_account()})
        for i in range(1,4):
            lottery.enter({'from':get_account(index = i), 'value': lottery.getEntranceFee()})
        ##this unit test is drastically close to being an integration test
        ##in this, we have to pretend to be a chainlink node, so as to call the function("callbackwithRandomness") presentin the mock contract"VRFCoordinatorMock"
        ##we will be using events, they are not accessible by the smart contracts but are much more gas efficient
        ##events can help us encounter when did we enter the calculating winner stage
        fund_with_link(lottery)
        starting_balance_of_account = get_account(index = 2).balance()
        balance_of_lottery = lottery.balance()
    
        transaction = lottery.end_lottery({'from':get_account()})
        request_id = transaction.events['RequestedRandomness']['requestId']
        ##eevents are helpful maily to understand when things are updated/upgraded/modified in the smart contract

        STATIC_RNG = 94237
        ###the above is the chosen random number

        local_vrf_coord = get_contract('vrf_coordinator')
        local_vrf_coord.callBackWithRandomness(
            request_id,
            STATIC_RNG,
            lottery.address,
            {'from':get_account()}
        )
        assert (lottery.recentWinner()) == (get_account(index = 2))
        assert lottery.balance() == 0
        assert get_account(index = 2).balance() == starting_balance_of_account + balance_of_lottery
        ##the above function call and parameterising... is how we mock responses from the blockchain...

#def main():
#    test_get_entrance_fee()
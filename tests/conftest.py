"""
Reusable client for API tests
"""
import os
import json
import pytest
import web3
from web3 import Web3
import computable # we use this to get the path to the contract abi/bin in the installed lib (rather than copy/paste them)
from computable.contracts import EtherToken
# import app

# setup deployed protocol
@pytest.fixture(scope="module")
def test_provider():
    return Web3.EthereumTesterProvider()

@pytest.fixture(scope="module")
def w3(test_provider):
    instance = Web3(test_provider)
    instance.eth.defaultAccount = instance.eth.accounts[0]
    return instance

# TODO this will be removed when computable.py updates next (contract changes, no args for ether_token construction)
@pytest.fixture(scope="module")
def ether_token_opts():
    return {'init_bal': Web3.toWei(1, 'ether')}

@pytest.fixture(scope="module")
def ether_token(w3, ether_token_opts):
    # this might be kind of a hack - but its a damn cool one
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'ethertoken', 'ethertoken.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'ethertoken', 'ethertoken.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    # TODO this must change on computable.py next update
    tx_hash = deployed.constructor(w3.eth.defaultAccount, ether_token_opts['init_bal']).transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = EtherToken(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

#  @pytest.fixture(scope="module")
#  def client():
    #  """
    #  Flask client for testing
    #  """
    #  app.app.config['TESTING'] = True
    #  app.initialize_app(app.app)
    #  client = app.app.test_client()
    #  yield client

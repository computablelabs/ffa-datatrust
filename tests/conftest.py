"""
Reusable client for API tests
"""

import pytest
import web3
from web3 import Web3
import app

# setup deployed protocol
@pytest.fixture(scope="module")
def test_provider():
    return Web3.EthereumTesterProvider()


@pytest.fixture(scope="module")
def w3(test_provider):
    instance = Web3(test_provider)
    instance.eth.defaultAccount = instance.eth.accounts[0]
    return instance

@pytest.fixture(scope="module")
def client():
    """
    Flask client for testing
    """
    app.app.config['TESTING'] = True
    app.initialize_app(app.app)
    client = app.app.test_client()
    yield client

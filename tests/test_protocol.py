"""
Tests for protocol interaction
"""
import pytest

def test_w3(w3):
    """
    Is web3 correctly setup for testing?
    """
    assert w3.eth.defaultAccount == w3.eth.accounts[0]

def test_ether_token(w3, ether_token):
    """
    did the ether token deploy correctly?
    """
    assert len(ether_token.account) == 42
    assert len(ether_token.address) == 42
    assert ether_token.account != ether_token.address

"""
Tests for protocol interaction
"""
import pytest

def test_w3(w3):
    """
    Is web3 correctly setup for testing?
    """
    assert w3.eth.defaultAccount == w3.eth.accounts[0]

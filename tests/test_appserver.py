"""
Tests for app.py
"""
import json
import sys
import pytest
# from mock import patch, Mock
# from moto import mock_secretsmanager
# sys.modules['settings'] = Mock()
import app
import constants

def get_dict(remove=None):
    the_data = dict(
        listing_hash='0xfoo',
        tx_hash='0xbar',
        title='asdf',
        description='htns',
        license='gcrl',
        file_type='qjkx',
        md5_sum='bmwv')

    if remove is not None:
        del the_data[remove]

    return the_data

def test_health(client):
    """
    Test that the /api/health/ endpoint returns OK for HTTP GET
    """
    rv = client.get('/api/health/')
    assert b'OK' in rv.data

#  def test_get_listings_success(client):
    #  get_listings = client.get('/api/v1/listings/')
    #  listings = json.loads(get_listings.data)
    #  assert get_listings.status_code == 200

#  def test_listings_post_success(client):
    #  post_listing = client.post('/api/v1/listings/', data=get_dict())
    #  assert post_listing.status_code == 201
    #  res = json.loads(post_listing.data.decode('UTF-8'))
    #  assert constants.NEW_CANDIDATE_SUCCESS == res['message']

def test_listings_post_missing_listing_hash(client):
    post_listing = client.post('/api/v1/listings/', data=get_dict('listing_hash'))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'listing_hash')

def test_listings_post_missing_tx_hash(client):
    post_listing = client.post('/api/v1/listings/', data=get_dict('tx_hash'))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'tx_hash')

def test_listings_post_missing_title(client):
    post_listing = client.post('/api/v1/listings/', data=get_dict('title'))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'title')

def test_listings_post_missing_description(client):
    post_listing = client.post('/api/v1/listings/', data=get_dict('description'))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'description')

def test_listings_post_missing_license(client):
    post_listing = client.post('/api/v1/listings/', data=get_dict('license'))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'license')

def test_listings_post_missing_file_type(client):
    post_listing = client.post('/api/v1/listings/', data=get_dict('file_type'))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'file_type')

def test_listings_post_missing_md5_sum(client):
    post_listing = client.post('/api/v1/listings/', data=get_dict('md5_sum'))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'md5_sum')

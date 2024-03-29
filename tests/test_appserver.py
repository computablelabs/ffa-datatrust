"""
Tests for app.py
"""
import json
import sys
import pytest
from mock import patch, Mock
# from moto import mock_secretsmanager
# sys.modules['settings'] = Mock()
import app
import constants

def test_health(client):
    """
    Test that the /api/health/ endpoint returns OK for HTTP GET
    """
    rv = client.get('/api/health/')
    assert b'OK' in rv.data

def test_get_listings_success(client):
    get_listings = client.get('/api/v1/listings/')
    listings = json.loads(get_listings.data)
    assert get_listings.status_code == 200

def test_listings_post_success(client):
    post_listing = client.post('/api/v1/listings/', data=dict(
        listing_hash='foo',
        title='asdf',
        description='asdf',
        license='asdf',
        file_type='asdf',
        md5_sum='asdf'
    ))
    assert post_listing.status_code == 201
    res = json.loads(post_listing.data.decode('UTF-8'))
    assert constants.NEW_CANDIDATE_SUCCESS == res['message']

def test_listings_post_missing_title(client):
    post_listing = client.post('/api/v1/listings/', data=dict(
        listing_hash='asdf',
        description='asdf',
        license='asdf',
        file_type='asdf',
        md5_sum='asdf'
    ))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'title')

def test_listings_post_missing_description(client):
    post_listing = client.post('/api/v1/listings/', data=dict(
        listing_hash='foo',
        title='asdf',
        license='asdf',
        file_type='asdf',
        md5_sum='asdf'
    ))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'description')

def test_listings_post_missing_license(client):
    post_listing = client.post('/api/v1/listings/', data=dict(
        listing_hash='foo',
        title='asdf',
        description='asdf',
        file_type='asdf',
        md5_sum='asdf'
    ))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'license')

def test_listings_post_missing_file_type(client):
    post_listing = client.post('/api/v1/listings/', data=dict(
        listing_hash='foo',
        title='asdf',
        description='asdf',
        license='asdf',
        md5_sum='asdf'
    ))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'file_type')

def test_listings_post_missing_md5_sum(client):
    post_listing = client.post('/api/v1/listings/', data=dict(
        listing_hash='foo',
        title='asdf',
        description='asdf',
        license='asdf',
        file_type='asdf'
    ))
    response = json.loads(post_listing.data)
    assert post_listing.status_code == 400
    assert response['message'] == (constants.MISSING_PAYLOAD_DATA % 'md5_sum')

from flask_restplus import fields
from api.restplus import api

health = api.model('Health check', {
    'status': fields.String(required=True, description='Overall status of application')
})

listing = api.model('Listing', {
    'listing_hash': fields.String(required=True, description='The listing this upload belongs to')
})

pagination = api.model('Page results descriptor', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results')
})

list_of_listings = api.inherit('List of listings', pagination, {
    'items': fields.List(fields.Nested(listing))
})
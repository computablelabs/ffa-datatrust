import logging

from flask import request
from flask_restplus import Resource
from api.restplus import api
from api.v1.serializers import listing, list_of_listings
from api.v1.parsers import pagination_arguments

log = logging.getLogger(__name__)

ns = api.namespace('v1/listings', description='Manage FFA Listings in the Datatrust')


@ns.route('/')
class Listing(Resource):

    @api.expect(pagination_arguments)
    @api.marshal_with(list_of_listings)
    def get(self):
        """
        Return a list of listings
        """
        args = pagination_arguments.parse_args(request)
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)

        listings = ''
        return listings
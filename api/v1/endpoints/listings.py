import hashlib
import os
import time
import logging.config
import boto3
from flask import request
from flask_restplus import Resource

import constants
import settings
from api.restplus import api
from api.v1.serializers import list_of_listings, new_listing
from api.v1.parsers import endpoint_arguments, listing_arguments
from datastore import dynamo
from protocol import deployed

LOGGING_CONFIG = os.path.join(settings.ROOT_DIR, 'logging.conf')
logging.config.fileConfig(LOGGING_CONFIG)
log = logging.getLogger()

ns = api.namespace('v1/listings', description='Manage FFA Listings in the Datatrust')


@ns.route('/', methods=['GET', 'POST'])
class Listings(Resource):
    @api.expect(endpoint_arguments)
    @api.marshal_with(list_of_listings)
    def get(self):
        """
        Return a list of listings
        """
        # args = endpoint_arguments.parse_args(request)
        # page = args.get('page', 1)
        # per_page = args.get('per_page', 10)
        db = dynamo.dynamo_conn
        listings = db.get_all_listings()
        print(listings)
        return {'items': listings}, 200

@ns.route('/<listing_hash>', methods=['POST'])
class Listing(Resource):
    @api.expect(listing_arguments)
    @api.marshal_with(new_listing)
    @api.response(201, constants.NEW_LISTING_SUCCESS)
    @api.response(400, constants.MISSING_PAYLOAD_DATA)
    @api.response(500, constants.SERVER_ERROR)
    def post(self, listing_hash):
        """
        Persist a new listing to file storage, db, and protocol
        """
        timings = {}
        start_time = time.time()
        payload = {}
        payload['listing'] = listing_hash
        uploaded_md5 = None
        for item in ['title', 'description', 'license', 'file_type', 'md5_sum']:
            if not request.form.get(item):
                api.abort(400, (constants.MISSING_PAYLOAD_DATA % item))
            else:
                payload[item] = request.form.get(item)
        if request.form.get('tags'):
            payload['tags'] = [x.strip() for x in request.form.get('tags').split(',')]
        for item in request.files.items():
            destination = os.path.join('/tmp/uploads/')
            log.info(f'Saving {item[0]} to {destination}')
            if not os.path.exists(destination):
                os.makedirs(destination)
            item[1].save(f'{destination}{item[0]}')
            uploaded_md5 = deployed.create_file_hash(f'{destination}{item[0]}')
            if uploaded_md5 != payload['md5_sum']:
                api.abort(500, (constants.SERVER_ERROR % 'file upload failed'))
            local_finish = time.time()
            timings['local_save'] = local_finish - start_time
            log.info(f'Saving {item[0]} to S3 bucket ffa-dev')
            s3 = boto3.client('s3')
            with open(f'{destination}{item[0]}', 'rb') as data:
                s3.upload_fileobj(data, 'ffa-dev', item[0])
            timings['s3_save'] = time.time() - local_finish
            os.remove(f'{destination}{item[0]}')
        log.info(timings)
        db = dynamo.dynamo_conn
        db_entry = db.add_listing(payload)
        if db_entry == constants.DB_SUCCESS:
            return {'message': constants.NEW_LISTING_SUCCESS}, 201

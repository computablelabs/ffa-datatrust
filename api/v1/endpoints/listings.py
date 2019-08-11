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


@ns.route('/', methods=['GET'])
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

@ns.route('/', methods=['POST'])
class Listing(Resource):
    @api.expect(listing_arguments)
    @api.marshal_with(new_listing)
    @api.response(201, constants.NEW_CANDIDATE_SUCCESS)
    @api.response(400, constants.MISSING_PAYLOAD_DATA)
    @api.response(428, constants.INVALID_CANDIDATE_OR_POLL_CLOSED)
    @api.response(500, constants.SERVER_ERROR)
    def post(self):
        """
        Persist a new listing to file storage, db, and protocol
        """
        is_datatrust = deployed.get_backend_address()
        if not is_datatrust:
            api.abort(500, 'This server is not the approved datatrust. New candidates not allowed')
        timings = {}
        start_time = time.time()
        payload = {}
        uploaded_md5 = None
        data_hash = None
        for item in ['title', 'description', 'license', 'file_type', 'md5_sum', 'listing_hash']:
            if not request.form.get(item):
                api.abort(400, (constants.MISSING_PAYLOAD_DATA % item))
            else:
                payload[item] = request.form.get(item)
                if request.form.get('tags'):
                    payload['tags'] = [x.strip() for x in request.form.get('tags').split(',')]
                    filenames = []
        owner = deployed.validate_candidate(payload['listing_hash'])
        if owner is None:
            api.abort(428, constants.INVALID_CANDIDATE_OR_POLL_CLOSED)
        payload['owner'] = owner
        md5_sum = request.form.get('md5_sum')
        if request.form.get('filenames'):
            filenames = request.form.get('filenames').split(',')
        for idx, item in enumerate(request.files.items()):
            destination = os.path.join('/tmp/uploads/')
            filename = filenames[idx] if idx < len(filenames) else item[0]
            log.info(f'Saving {filename} to {destination}')
            if not os.path.exists(destination):
                os.makedirs(destination)
            item[1].save(f'{destination}{filename}')
            with open(f'{destination}{filename}', 'rb') as data:
                contents = data.read()
                uploaded_md5 = hashlib.md5(contents).hexdigest()
            if uploaded_md5 != md5_sum:
                api.abort(500, (constants.SERVER_ERROR % 'file upload failed'))
            local_finish = time.time()
            timings['local_save'] = local_finish - start_time
            log.info(f'Saving {filename} to S3 bucket {settings.S3_DESTINATION}')
            s3 = boto3.client('s3')
            with open(f'{destination}{filename}', 'rb') as data:
                # apparently this overwrites existing files.
                # something to think about?
                s3_filename = f"{owner}/{constants.S3_CANDIDATE}/{filename}"
                s3.upload_fileobj(data, settings.S3_DESTINATION, s3_filename)
            timings['s3_save'] = time.time() - local_finish
            data_hash = deployed.create_file_hash(f'{destination}{filename}')
            os.remove(f'{destination}{filename}')
        log.info(timings)
        db = dynamo.dynamo_conn
        db_entry = db.add_listing(payload)
        if db_entry == constants.DB_SUCCESS:
            try:
                deployed.send_data_hash(payload['listing_hash'], data_hash)
                return {'message': constants.NEW_CANDIDATE_SUCCESS}, 201
            except ValueError as err:
                api.abort(428, err)

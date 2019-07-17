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
from api.v1.serializers import list_of_listings
from api.v1.parsers import endpoint_arguments, listing_arguments

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
        args = endpoint_arguments.parse_args(request)
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)

        listings = ''
        return listings

@ns.route('/<listing_hash>', methods=['POST'])
class Listing(Resource):
    @api.expect(listing_arguments)
    @api.response(201, 'Listing successfully added')
    @api.response(500, 'Listing failed due to server side error')
    def post(self, listing_hash):
        """
        Persist a new listing to file storage, db, and protocol
        """
        timings = {}
        start_time = time.time()
        title = None
        description = None
        owner = None
        file_type = None
        md5_sum = None
        tags = None
        uploaded_md5 = None
        for item in ['title', 'description', 'license', 'file_type', 'md5_sum']:
            if not request.form.get(item):
                api.abort(400, (constants.MISSING_PAYLOAD_DATA % item))
        if request.form.get('tags'):
            tags = request.form.get('tags')
        for item in request.files.items():
            destination = os.path.join('/tmp/uploads/')
            log.info(f'Saving {item[0]} to {destination}')
            if not os.path.exists(destination):
                os.makedirs(destination)
            item[1].save(f'{destination}{item[0]}')
            with open(f'{destination}{item[0]}', 'rb') as data:
                contents = data.read()
                uploaded_md5 = hashlib.md5(contents).hexdigest()
            if uploaded_md5 != md5_sum:
                return 'File upload failed', 500
            local_finish = time.time()
            timings['local_save'] = local_finish - start_time
            log.info(f'Saving {item[0]} to S3 bucket ffa-dev')
            s3 = boto3.client('s3')
            with open(f'{destination}{item[0]}', 'rb') as data:
                s3.upload_fileobj(data, 'ffa-dev', item[0])
            timings['s3_save'] = time.time() - local_finish
            os.remove(f'{destination}{item[0]}')
        log.info(timings)
        return 'You uploaded a file'

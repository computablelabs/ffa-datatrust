from werkzeug.datastructures import FileStorage
from flask_restplus import reqparse

endpoint_arguments = reqparse.RequestParser()
endpoint_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
endpoint_arguments.add_argument('bool', type=bool, required=False, default=1, help='Page number')
endpoint_arguments.add_argument('per_page', type=int, required=False, choices=[2, 10, 20, 30, 40, 50],
                                  default=10, help='Results per page {error_msg}')
endpoint_arguments.add_argument('file', type=FileStorage, location='files',
                                  required=False, help='Listing asset')

listing_arguments = reqparse.RequestParser(bundle_errors=True)
listing_arguments.add_argument('file_upload', type=FileStorage, required=True, location='files', help='Listing file asset')
listing_arguments.add_argument('file_type', type=str, required=True, location='form', help='File type: image, video, audio, etc')
listing_arguments.add_argument('md5_sum', type=str, required=True, location='form', help='MD5 of file asset')
listing_arguments.add_argument('tags', type=str, required=False, location='form', action='split', help='Comma delimited list of tags for discovery')

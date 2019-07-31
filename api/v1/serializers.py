from flask_restplus import fields
from api.restplus import api

health = api.model('Health check', {
    'status': fields.String(required=True, description='Overall status of application')
})

new_listing = api.model('NewListing', {
    'message': fields.String(required=True, description='Server response for a new listing')
})

listing = api.model('Listing', {
    'description': fields.String(required=True, description='Description of listing item'),
    'title': fields.String(required=True, description='Title of the listing'),
    'license': fields.String(required=True, description='Usage license'),
    'listing': fields.String(required=True, description='The listing this upload belongs to'),
    'file_upload': fields.String(required=False, description='File asset for a listing submitted as form-data'),
    'file_type': fields.String(required=True, description='File content: video, image, audio, etc'),
    'md5_sum': fields.String(required=True, description='md5 sum of the file being uploaded'),
    'tags': fields.List(fields.String, required=False, description='Tags to categorize and describe the listing file')
})

pagination = api.model('Page results descriptor', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results')
})

list_of_listings = api.inherit('List of listings', {
    'items': fields.List(fields.Nested(listing))
})
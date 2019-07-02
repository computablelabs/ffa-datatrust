import logging

from flask import request
from flask_restplus import Resource
from api.restplus import api
from api.v1.serializers import health

log = logging.getLogger(__name__)

ns = api.namespace('health', description='Application server healthcheck')

@ns.route('/')
class HealthCheck(Resource):

    @api.marshal_with(health)
    def get(self):
        """
        Return results of healthcheck
        """
        health_check = {}
        health_check['status'] = 'OK'
        return health_check

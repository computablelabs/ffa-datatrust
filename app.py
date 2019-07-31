import logging.config

import boto3
from botocore.exceptions import ClientError
from flask import Flask, Blueprint
import json
import os

import settings
from api.v1.endpoints.health import ns as health_namespace
from api.v1.endpoints.listings import ns as listings_namespace
from api.restplus import api
from datastore import dynamo
from protocol import deployed

def configure_app(flask_app):
    """
    Initial app setup. Get secrets from AWS, initialize FFA Datatrust
    :param flask_app: the flask app
    :return: the same flask app, plus config details
    """
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['FLASK_PORT'] = settings.FLASK_PORT
    flask_app.config['ROOT_DIR'] = settings.ROOT_DIR
    flask_app.config['DB_URL'] = settings.DB_URL
    flask_app.config['TABLE_NAME'] = settings.TABLE_NAME
    flask_app.config['S3_DESTINATION'] = settings.S3_DESTINATION
    if os.getenv('ENV') != 'dev':
        app.config.SWAGGER_VALIDATOR_URL = f"https://ffa{os.getenv('ENV')}.computablelabs.com/api/"

def initialize_app(flask_app):
    """
    Initialize Flask
    :param flask_app: the flask application
    :return: the same flask application, initialized
    """
    configure_app(flask_app)
    db = dynamo.dynamo_conn
    db.init_db(
        flask_app.config['DB_URL'],
        flask_app.config['TABLE_NAME'],
        'us-west-1'
    )
    deployed.init_protocol(
        settings.RPC_PATH,
        settings.DATATRUST_CONTRACT,
        settings.DATATRUST_HOST,
        settings.VOTING_CONTRACT,
        settings.DATATRUST_KEY,
        settings.DATATRUST_WALLET
    )
    deployed.initialize_datatrust()

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(health_namespace)
    api.add_namespace(listings_namespace)
    flask_app.register_blueprint(blueprint)

def main():
    initialize_app(app)
    app.run(debug=settings.FLASK_DEBUG, host='0.0.0.0', port=app.config['FLASK_PORT'])

app = Flask(__name__)
LOGGING_CONFIG = os.path.join(settings.ROOT_DIR, 'logging.conf')
logging.config.fileConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)

if __name__ == '__main__':
    main()

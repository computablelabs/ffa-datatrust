import logging.config

import os
import json
import boto3
from botocore.exceptions import ClientError
from flask import Flask, Blueprint
import settings
from api.v1.endpoints.health import ns as health_namespace
from api.v1.endpoints.listings import ns as listings_namespace
from api.restplus import api

app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)

def get_secret():
    """
    Retrieve application secrets from AWS Secrets Manager
    """
    secret_name = f"ffa/datatrust/{os.getenv('ENV', 'dev')}"
    region_name = 'us-west-1'

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        logging.info("Retrieving secrets for {}".format(secret_name))
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            logging.error('Task does not have access to the keys in KMS')
            raise e
        else:
            # Raise anything we didn't catch
            raise e
    else:
        return json.loads(get_secret_value_response['SecretString'])

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
    for k,v in get_secret().items():
        flask_app.config[k] = v

def initialize_app(flask_app):
    """
    Initialize Flask
    :param flask_app: the flask application
    :return: the same flask application, initialized
    """
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(health_namespace)
    api.add_namespace(listings_namespace)
    flask_app.register_blueprint(blueprint)

def main():
    initialize_app(app)
    app.run(debug=settings.FLASK_DEBUG, host='0.0.0.0', port=app.config['FLASK_PORT'])

if __name__ == '__main__':
    main()

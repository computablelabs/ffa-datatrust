import os
import json
import boto3
from botocore.exceptions import ClientError

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
            raise e
        else:
            # Raise anything we didn't catch
            raise e
    else:
        return json.loads(get_secret_value_response['SecretString'])

secrets = get_secret()
# Flask settings
FLASK_DEBUG = True  # Do not use debug mode in production
FLASK_PORT = 5000

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Application settings
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_URL = secrets['DB_URL']
TABLE_NAME = secrets['TABLE_NAME']
S3_DESTINATION = secrets['S3_DESTINATION']
CELERY_RESULT_BACKEND = secrets['CELERY_RESULT_BACKEND']
CELERY_BROKER_URL = secrets['CELERY_BROKER_URL']

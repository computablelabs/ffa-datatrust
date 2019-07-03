"""
Deployment script for stack
"""

import sys
import boto3
from botocore.exceptions import ClientError
import json

STACK_NAME = 'ffa-datatrust-staging'

def get_secrets(session, secret_id):
    """
    Get stack secrets from AWS Secrets Manager
    :param session: boto3 session
    :param secret_id: string
    :return: dict
    """
    secretsmanager = session.client('secretsmanager')
    secrets = json.loads(secretsmanager.get_secret_value(SecretId=secret_id)['SecretString'])
    formatted_secrets = []
    for (key, value) in secrets.items():
        if key != 'TABLE_NAME' and key != 'DB_URL':
            formatted_secrets.append(
                {"ParameterKey": key, "ParameterValue": value}
            )
    formatted_secrets.append(
        {"ParameterKey": "StackName", "ParameterValue": STACK_NAME}
    )
    return formatted_secrets


def deploy_stack(session, secrets):
    """
    Deploy the stack using CloudFormation
    :param session: AWS boto3 session
    :param secrets: Stack secrets
    :return:
    """
    with open('scripts/cf_stack.yml') as template:
        template_data = template.read()
        try:
            cloudformation = session.client('cloudformation')
            stack = cloudformation.update_stack(
                StackName=STACK_NAME,
                TemplateBody=template_data,
                Parameters=secrets
            )
            print(stack)
        except ClientError as ex:
            error_message = ex.response['Error']['Message']
            if error_message.endswith('does not exist'):
                print('Stack does not exist, creating')
                stack = cloudformation.create_stack(
                    StackName=STACK_NAME,
                    TemplateBody=template_data,
                    Parameters=secrets
                )
                print(stack)
            else:
                raise


if len(sys.argv) == 2:
    session = boto3.session.Session(
        profile_name=sys.argv[1]
    )
else:
    session = boto3.session.Session()

deploy_stack(
    session,
    get_secrets(session, 'ffa/datatrust/staging')
)

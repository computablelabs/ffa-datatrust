"""
Connection manager for DynamoDB
"""
import boto3
from botocore.exceptions import ClientError

import constants

class DynamoDBConn():
    def init_db(self, db_url, table_name, region):
        self.db = boto3.resource('dynamodb', region, endpoint_url=db_url)
        self.table_name = table_name

    def get_all_listings(self):
        """
        Return all db listings
        Future versions will support paging, offsets, and search parameters
        :return: dict
        """
        table = self.db.Table(self.table_name)
        response = table.scan()
        return response['Items']

    def get_listing(self, payload):
        """
        Return a listing from the database
        :param payload: dict
        :return: dict
        """
        try:
            table = self.db.Table(self.table_name)
            response = table.get_item(
                Key={
                    'listing': payload['listing']
                }
            )
            if 'Item' in response:
                return response['Item']
            else:
                return constants.ITEM_NOT_FOUND
        except Exception as exc:
            print(exc)
            return constants.DB_ERROR

    def add_listing(self, payload):
        """
        Add a listing to the table
        :param payload: dict
        :return: string
        """
        try:
            table = self.db.Table(self.table_name)
            response = table.put_item(
                Item=payload
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return constants.DB_SUCCESS
            else:
                return constants.DB_ERROR
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'ValidationException':
                return 'ValidationException'
                # TODO: Add 'data' array to db schema
            else:
                raise

dynamo_conn = DynamoDBConn()

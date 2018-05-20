#!/usr/bin/env
"""
This is a test script for LambdaExecuteEcsTask.py. The test will mock S3 and store object in the bucket.
It will then invoke an event for the lambda function for the updated bucket key
"""
import os
import sys
import json
import base64
import boto3
from moto import mock_ecs, mock_s3, mock_lambda

REGION = 'us-east-1'

# test for creating a lambda function from a SAM template
#    - test using aws cloudformation

# test for invoking a lambda function by creating a new object created event in S3
#    - create S3 bucket, upload file to it
#    - invoke lambda function by passing the bucket and key in the event


def test_deploy_sam_template(template_filepath):
    pass



# TODO - how? using this?
def test_fake_s3(endpoint_url):
    # TODO - start fake S3 server
    s3_client = boto3.client('s3', aws_access_key_id='a', aws_secret_access_key='b', endpoint_url=endpoint_url)
    s3_client.create_bucket(Bucket='fake-bucket')
    s3_client.create_bucket(Bucket='fake-bucket-1')
    s3_client.list_buckets()


def test_s3_event_lambda_function():
    # put a file in S3 bucket with task ARNs
    # create lambda function
    # send test event as S3 bucket and prefix    #
    pass


def _upload_file_to_bucket(upload_filepath, bucket, upload_filename):
    s3_client = boto3.client('s3', region_name=REGION)
    if bucket not in s3_client.list_buckets():
        s3_client.create_bucket(Bucket=bucket)
    s3_res = boto3.resource('s3')
    s3_res.meta.client.upload_file(upload_filepath, bucket, upload_filename)


def _create_lambda_function(name, handler, role, code, bucket):
    """

    :param name:
    :param handler:
    :param role:
    :param code: zipfile containing python code for lambda functions
    :param bucket:
    :return:
    """
    client = boto3.client('lambda', region_name=REGION)
    client.create_function(
        FunctionName=name,
        Runtime='python2.7',
        Role=role,
        Handler=handler,
        Code={
            'S3Bucket': bucket,
            'S3Key': code
        },
        Description='function created using automation',
        Timeout=3,
        MemorySize=128,
        Publish=True
    )


def _invoke_lambda_function(name, payload):
    client = boto3.client('lambda', region_name=REGION)
    result = client.invoke(FunctionName=name, InvocationType='RequestResponse', Payload=payload)
    print 'StatusCode = {}'.format(result["StatusCode"])
    print 'LogResult = {}'.format(base64.b64decode(result["LogResult"]).decode('utf-8'))
    print 'Payload = {}'.format(result["Payload"].read().decode('utf-8'))


@mock_lambda
@mock_s3
def test_LambdaExecuteEcsTask():
    """
    STEPS:
    - upload python file to S3
    - create lambda function from python file
    - create task defs and file containing task ARNs
    - upload task ARN file in S3
    - invoke lambda function using S3 event containing the task ARN file CreateObject
    """

    bucket_name = 'testamolbucket'
    python_lambda_zip = r'C:\Users\aakokje\Documents\cambia\aws_sam_exercise\test\tests\inputs\mylambdafile.zip'
    python_lambda_zip_file = python_lambda_zip.split("\\")[-1]
    lambda_execution_role = 'arn:aws:iam::358839596884:role/test-amol-role-lambda'
    payload_data = {'key0': 'value0'}
    event_payload = json.dumps(payload_data)

    _upload_file_to_bucket(python_lambda_zip, bucket_name, python_lambda_zip_file)
    _create_lambda_function('testfunction', 'mylambdafile.lambda_handler',
                            lambda_execution_role, python_lambda_zip_file, bucket_name)
    _invoke_lambda_function('testfunction', event_payload)



test_LambdaExecuteEcsTask()
##test_moto_s3()
#test_fake_s3() # fix this
"""
# THIS TEST IS NOT WORKING
test_sam_local('mybucket',
               'myprefix',
               r'C:\Users\aakokje\Documents\cambia\aws_sam_exercise\test\tests\outputs\test_lambda_list_0_sam.yaml',
               'mylambdafunctionname')
"""

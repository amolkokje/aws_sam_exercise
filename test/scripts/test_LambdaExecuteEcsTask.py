#!/usr/bin/env
"""
This is a test script for LambdaExecuteEcsTask.py. The test will mock S3 and store object in the bucket.
It will then invoke an event for the lambda function for the updated bucket key.
"""
import os
import time
import json
import base64
import boto3
import zipfile
from moto import mock_ecs, mock_s3, mock_lambda, mock_logs

REGION = 'us-east-1'


def _upload_file_to_bucket(upload_filepath, bucket, upload_filename):
    print 'Uploading file "{0}" to bucket "{1}" as "{2}"'.format(upload_filepath, bucket, upload_filename)
    s3_client = boto3.client('s3', region_name=REGION)
    if bucket not in s3_client.list_buckets():
        response = s3_client.create_bucket(Bucket=bucket)
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200, 'Invalid code. Response={0}'.format(response)
    s3_res = boto3.resource('s3')
    s3_res.meta.client.upload_file(upload_filepath, bucket, upload_filename)


def _create_lambda_function(name, handler, role, code, bucket):
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
    # add permissions to invoke by S3
    client.add_permission(
        Action='lambda:InvokeFunction',
        FunctionName='{0}'.format(name),
        Principal='s3.amazonaws.com',
        SourceAccount='123456789012',
        SourceArn='arn:aws:s3:::{0}/*'.format(bucket),
        StatementId='ID-1',
    )


def _invoke_lambda_function(name, payload):
    client = boto3.client('lambda', region_name=REGION)
    result = client.invoke(FunctionName=name, InvocationType='RequestResponse', Payload=payload)
    print 'StatusCode = {0}'.format(result["StatusCode"])
    print 'LogResult = {0}'.format(base64.b64decode(result["LogResult"]).decode('utf-8'))
    print 'Payload = {0}'.format(result["Payload"].read().decode('utf-8'))

    logs_conn = boto3.client('logs', region_name=REGION)
    start = time.time()
    while (time.time() - start) < 30:
        result = logs_conn.describe_log_streams(logGroupName='/aws/lambda/{0}'.format(name))
        log_streams = result.get('logStreams')
        if not log_streams:
            time.sleep(1)
            continue

        result = logs_conn.get_log_events(logGroupName='/aws/lambda/{0}'.format(name),
                                          logStreamName=log_streams[0]['logStreamName'])
        events = result.get('events')
        print 'no of events={0}, events={1}'.format(len(events), events)
        break


def test_fake_s3(fakes3_port):
    """
    to make this work, start fakes3 server first by executing on command line: fakeS3 server -p <PORT> --root=ROOT
    """
    s3_client = boto3.client('s3', aws_access_key_id='a', aws_secret_access_key='b',
                             endpoint_url='http://localhost:{0}'.format(fakes3_port))
    s3_client.create_bucket(Bucket='fake-bucket')
    s3_client.create_bucket(Bucket='fake-bucket-1')
    s3_client.list_buckets()


def test_lambda_execute_ecs_task(mock=False):
    """
    Test for lambda function that creates ecs tasks
    :param mock: True: tests using moto lib, False: tests using real cloud env (make sure you have your default creds
    set)
    :return:
    """
    ms3 = mock_s3()
    ml = mock_lambda()
    mecs = mock_ecs()
    mlogs = mock_logs()
    if mock:
        ms3.start()
        ml.start()
        mecs.start()
        mlogs.start()

    bucket_name = 'testamolbucket'
    key_name = 'taskarn.list'  # path to file that contains task ARNs
    script_dir = os.getcwd()
    lambda_function_filepath = r'..\..\scripts'
    lambda_function_file = 'LambdaExecuteEcsTask.py'
    assert os.path.exists(os.path.join(lambda_function_filepath, lambda_function_file)), 'File does not exist!'

    lambda_function_name = 'testfunction'
    lambda_execution_role = 'arn:aws:iam::123456789:role/test-amol-role-lambda'
    lambda_zip_file = '.'.join([lambda_function_file.split('.')[0], 'zip'])

    os.chdir(lambda_function_filepath)
    lambda_zip_filepath = r'..\test\outputs\{0}'.format(lambda_zip_file)
    with zipfile.ZipFile(lambda_zip_filepath, 'w') as myzip:
        myzip.write(lambda_function_file)
    _upload_file_to_bucket(lambda_zip_filepath, bucket_name, lambda_zip_file)
    _create_lambda_function(lambda_function_name, 'LambdaExecuteEcsTask.lambda_handler',
                            lambda_execution_role, lambda_zip_file, bucket_name)

    s3_event_payload_data = {'Records': [{
                                            's3': {
                                                'object':{'key':'testkey'},
                                                'bucket':{'name':bucket_name}
                                                }
                                          }
                                         ]
                             }

    os.chdir(script_dir)
    _upload_file_to_bucket(key_name, bucket_name, key_name)

    if not mock:
        # lambda function which uses boto lib cannot be mocked, but invoking the lambda can be mocked in any case
        # Note: This lambda function invocation has already been validated in real AWS environment.
        _invoke_lambda_function('testfunction', json.dumps(s3_event_payload_data))


#test_fake_s3(4569)
test_lambda_execute_ecs_task(mock=True)


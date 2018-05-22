import boto3
import os

"""
This is a very simple lambda function which only processes events received from S3 successfully. When triggered by an S3
event, it reads the key file where it expects the task def ARNs for the tasks to execute separated by new line. If the
task ARN is valid, it launches the task as 'FARGATE' launch type(for simplicity). Following configuration parameters
are read from the environment variables of the lambda function.
CLUSTER
SUBNETS
SECURITY_GROUPS
ASSIGN_PUBLIC_IP
"""

def lambda_handler(event, context):
    assert ('Records' in event.keys()) and \
           (event.get('Records')[0].get('s3')), 'Lambda Function is not triggered by an AWS S3 event!'
    key = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']

    s3_client = boto3.client('s3')
    object_data = s3_client.get_object(Bucket=bucket_name, Key=key)['Body'].read()

    ecs_client = boto3.client('ecs')
    ecs_taskdef_arns = ecs_client.list_task_definitions()['taskDefinitionArns']
    network_config = {'awsvpcConfiguration': {'subnets': [os.environ['SUBNETS']],
                                              'securityGroups': [os.environ['SECURITY_GROUPS']],
                                              'assignPublicIp': os.environ['ASSIGN_PUBLIC_IP']}}

    for task_arn in object_data.splitlines():
        task_arn = task_arn.strip()  # remove any unintentional spaces
        print 'Checking for Task Def ARN "{0}"'.format(task_arn)
        assert task_arn in ecs_taskdef_arns, 'Task ARN "{0}" does not exist ' \
                                             'in ECS Task Defs: {1}'.format(task_arn, ecs_taskdef_arns)
        print 'Task ARN is valid. Executing Task'
        print 'Run Task Response = {0}'.format(ecs_client.run_task(cluster=os.environ['CLUSTER'],
                                                                   taskDefinition=task_arn,
                                                                   launchType='FARGATE',
                                                                   networkConfiguration=network_config))
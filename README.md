# aws_sam_exercise
This project demonstrates how to test AWS lambda functions locally by mocking the AWS environment using Moto and FakeS3 libraries. After the lambda functions are tested in isolation, you can create SAM templates and test the invocation locally using sam local before deploying to your AWS account.

## scripts\ConvertLambdaToSamTemplate.py
Python script that takes a YAML defining Lambda functions and generate an AWS SAM template as a result. It should be executable via AWS SAM CLI.
Simple test script created: test\scripts\test_ConvertLambdaToSamTemplate.py. Execute test script in the test\scripts folder.

## scripts\LambdaExecuteEcsTask.py
Lambda that is responsible for executing an ECS task. The task ARN will be provided via an object within S3.
If the event that triggers the lambda function is a valid S3 event that is triggered by creation or update of a file in S3 bucket, then it will pull the list of task definition ARNs from the file, and execute a task for each. The file in S3 bucket should be a new-line separated list of task ARNs.
Simple test script created: test\scripts\test_LambdaExecuteEcsTask.py. Execute test script in the test\scripts folder.

You can use the file test\scripts\requirements.txt to generate your virtualenv or install on your box to run the scripts.




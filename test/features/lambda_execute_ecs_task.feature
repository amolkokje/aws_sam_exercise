Feature: Lambda Execute ECS Task

  Scenario: Lambda function standalone invocation with any event
    When I execute handler "lambda_handler" in file "LambdaExecuteEcsTask.py" with sample event payload
    Then I see error response

  Scenario: Lambda function standalone invocation with any event
    When I execute handler "lambda_handler" in file "LambdaExecuteEcsTask.py" with sample s3 payload
    Then I see no errors in reponse

  Scenario: Lambda invocation from S3 events
    Given Delete lambda function "LambdaExecuteEcsTask" if any
    And Create lambda permissions "testpermissions" for "s3" events from bucket "testbucket"
    And Create iam policy "testpolicy" to allow access to "s3,ecs,logs"
    And Create lambda function "LambdaExecuteEcsTask with permissions "testpermissions" and policy "testpolicy"
    Given Create "2" dummy tasks and upload file with task arns to bucket "testbucket"
    When I invoke lambda function with events from bucket "testbucket"
    Then I see no errors in cloudWatch logstream '/aws/lambda/LambdaExecuteEcsTask'
    And I see "2" tasks launched in ecs
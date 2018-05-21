#!/usr/bin/env
"""
This is a test script for convert_lambda_to_template.py. It will take input YAML files from the folder \tests and
dump the output files in the folder \results.
"""
import os
import sys
import subprocess
sys.path.append(r'..\..')
from scripts.convert_lambda_to_sam_template import convert_lambda_to_sam_template


def _runcmd(cmd):
    x = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return x.communicate(x.stdout)


def test_sam_cli_s3_event(bucket_name, prefix, template_filepath):
    cmd = 'sam local generate-event s3 --bucket {0} --key {1} | sam local invoke -t {2}'.format(bucket_name, prefix, template_filepath)
    print 'Executing command = {0}'.format(cmd)
    print 'Output = {0}'.format(_runcmd(cmd))


def test_sam_cli_events_file(template_filepath, event_filepath):
    cmd = 'sam local invoke -t {0} -e {1}'.format(template_filepath, event_filepath)
    print 'Executing command = {0}'.format(cmd)
    print 'Output = {0}'.format(_runcmd(cmd))


def test_convert_lambda_to_sam_template():
    # this will make sure to change path to \inputs directory which contains test inputs
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(r'..\inputs')

    # get test files
    test_yaml_files = []
    test_event_files = []
    for file in os.listdir(os.getcwd()):
        if file.endswith('.yaml'):
            test_yaml_files.append(file)
        if file.endswith('.json'):
            test_event_files.append(file)
    print 'Test yaml files = {}'.format(test_yaml_files)
    print 'Test event files = {}'.format(test_event_files)

    # iterate all tests
    for file in test_yaml_files:
        input_filepath = os.path.join(os.getcwd(), file)
        assert os.path.exists(file), 'Input yaml file path {0} does not exist!'.format(file)
        output_filepath = convert_lambda_to_sam_template(input_filepath)
        print 'Input={0}, Output={1}'.format(file, output_filepath)

        test_sam_cli_s3_event('mybucket', 'mybucketprefix', output_filepath)
        for event_file in test_event_files:
            #event_filepath = os.path.join(tests_folder, event_file)
            assert os.path.exists(event_file), 'Input event file path {0} does not exist!'.format(event_file)
            test_sam_cli_events_file(output_filepath, event_file)


test_convert_lambda_to_sam_template()
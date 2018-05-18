#!/usr/bin/env
"""
This is a test script for convert_lambda_to_template.py. It will take input YAML files from the folder \tests and
dump the output files in the folder \results.
"""
import os
import sys
sys.path.append(r'..\..')
from scripts.convert_lambda_to_sam_template import convert_lambda_to_sam_template

tests_folder = r'C:\Users\aakokje\Documents\cambia\aws_sam_exercise\test\tests'
test_files = ['test_lambda_list_0.yaml',
              'test_lambda_list_1.yaml']
for file in test_files:
    input_filepath = os.path.join(tests_folder, file)
    assert os.path.exists(input_filepath), 'Input file path {0} does not exist!'.format(input_filepath)
    output_filepath = convert_lambda_to_sam_template(input_filepath)
    print 'Input={0}, Output={1}'.format(input_filepath, output_filepath)

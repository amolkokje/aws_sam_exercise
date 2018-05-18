#!/usr/bin/env
"""
This script has modules that take in a YAML file defining Lambda functions and generate an AWS SAM template as a result.
Output file name is constructed from input file name <input_file_name>_sam.yaml.

There are two ways to use this script:
1. By specifying the yaml file as an input param'
   Example: python convert_lambda_to_sam_template.py -i test_file.yaml
   Output file is dumped in the folder \outputs.

2. By importing the module in your python script:
   Example:
    from convert_lambda_to_sam_template import convert_lambda_to_sam_template
    output_file_path = convert_lambda_to_sam_template(input_file_path)
"""
import os
import time
import yaml
import zipfile
from optparse import OptionParser

AWS_TEMPLATE_FORMAT_VERSION = '2010-09-09'
TRANSFORM = 'AWS::Serverless-2016-10-31'
DESCRIPTION = 'SAM Template generated via automation'
TYPE = 'AWS::Serverless::Function'

def convert_lambda_to_sam_template(input_filepath):
    assert os.path.exists(input_filepath), 'Input File Path {0} does not exist!'.format(input_filepath)

    output_dirname = os.path.join(os.path.dirname(input_filepath), 'outputs')
    output_filename = ''.join([os.path.basename(input_filepath).split('.')[0], '_sam.yaml'])
    output_filepath = os.path.join(output_dirname, output_filename)
    if not os.path.exists(output_dirname):
        os.makedirs(output_dirname)

    with open(input_filepath, 'r') as fh:
        input_yaml_data = yaml.load(fh.read())
    assert 'lambda_functions' in input_yaml_data, 'Key "functions" not defined in {0}'.format(input_filepath)
    lambda_function_list = input_yaml_data['lambda_functions']

    sam_template_yaml = {'AWSTemplateFormatVersion': AWS_TEMPLATE_FORMAT_VERSION,
                         'Transform': TRANSFORM,
                         'Description': DESCRIPTION + ' at {0}'.format(time.strftime('%c')),
                         'Resources': {}
                         }

    """
    AMOL: In the example provided in the test, the Sample SAM template points CodeUri to bundle.zip. To ensure that
    this code works for real scenarios, I am assuming that the lambda package needs to be created by this script. So
    I have added checks to ensure that the python file specified in the input YAML exists and if it does, zip it to
    specify as CodeUri in the output SAM template.
    Assumption: We make sure that the file has the required handler/method.
    """
    for function in lambda_function_list:
        lambda_code = function['lambda_code']
        assert os.path.exists(lambda_code), 'Lambda code file {0} does not exist!'.format(lambda_code)
        code_uri_file = ''.join([lambda_code.split('.')[0], '.zip'])
        with zipfile.ZipFile(code_uri_file, 'w') as myzip:
            myzip.write(lambda_code)

        sam_template_yaml['Resources'][function['function_name']] = {'Type': TYPE,
                                                                     'Properties': {'Handler': function['handler'],
                                                                                    'Runtime': function['runtime'],
                                                                                    'CodeUri': code_uri_file}}
    with open(output_filepath, 'w') as fh:
        yaml.dump(sam_template_yaml, fh, default_flow_style=False)
    return output_filepath

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='input_filepath', help='input .yaml file containing lambda functions')
    (options, args) = parser.parse_args()
    if not options.input_filepath:
        raise RuntimeError('Mandatory input parameter -i is required!')
    convert_lambda_to_sam_template(options.input_filepath)

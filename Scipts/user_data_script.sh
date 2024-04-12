#!/bin/bash

# Install AWS CLI v3
yum install -y aws-cli

s3_output_bucket_name="{s3_output_bucket_name}"

# Read the input text and input file path from DynamoDB
response=$(aws dynamodb get-item \
--table-name poctable \
--key '{"id": {"S": "{id}"}}' \
--projection-expression 'input_text, input_file_path')

# Extract input text and input file path from the response
input_text=$(echo $response | jq -r '.Item.input_text.S')
input_file_path=$(echo $response | jq -r '.Item.input_file_path.S')

# Extract the file name without extension
input_file_name=$(basename "$input_file_path" | cut -d'.' -f1)

output_file_name="${input_file_name}_{id}_output.txt"


# Download input file from S3
aws s3 cp $input_file_path /tmp/input_file.txt


# Append input text to the input file and save as output file
echo " : $input_text" >> /tmp/input_file.txt
cp /tmp/input_file.txt /tmp/output_file.txt

s3_output_path="s3://$s3_output_bucket_name/$output_file_name"

# Upload output file to S3
aws s3 cp /tmp/output_file.txt $s3_output_path

# Save the output file path in DynamoDB FileTable
aws dynamodb update-item --table-name poctable \
--key '{"id": {"S": "{id}"}}' \
--update-expression 'SET output_file_path = :path' \
--expression-attribute-values '{":path":{"S":"'"$s3_output_path"'"}}'

# Terminate the instance
shutdown -h now
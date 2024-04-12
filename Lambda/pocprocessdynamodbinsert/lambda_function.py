import json
import boto3

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            # Get the new item from the DynamoDB stream record
            new_item = record['dynamodb']['NewImage']
            
            id_str = new_item['id']['S']
            
            print("Dynamodb table item to process:", id_str)
            
            # Process the new item
            process_new_item(id_str)
    
    return {
        'statusCode': 200,
        'body': json.dumps('DynamoDB stream event processing complete')
    }

def download_file_from_s3(bucket_name, file_key):
    s3 = boto3.client('s3')
    
    try:
        # Download the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        # Read the contents of the file
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return None


def get_config_values_from_ssm():
    ssm_client = boto3.client('ssm')
    
    try:
        
        # Retrieve parameter values starting with '/pocproject/'
        response = ssm_client.get_parameters_by_path(
            Path='/pocproject/',
            Recursive=True,
            WithDecryption=True  
        )
        
        parameter_values = {}
        for parameter in response['Parameters']:
            parameter_name = parameter['Name']
            parameter_value = parameter['Value']
            parameter_values[parameter_name] = parameter_value
            
        return parameter_values
        
    except Exception as e:
        print(f"Error Getting parameters from SSM: {e}")
        return None


def process_new_item(id):
    
    conf = get_config_values_from_ssm()

    # Parameters
    bucket_name = conf['/pocproject/bucket_name']
    script_name = conf['/pocproject/script_name']
    instance_type = conf['/pocproject/instance_type']
    key_name = conf['/pocproject/key_name']
    ami_id = conf['/pocproject/ami_id']

    # Download the file from S3 and update the id and s3 bucket parameters
    user_data_script = download_file_from_s3(bucket_name, script_name).replace("{id}", id)
    user_data_script = user_data_script.replace("{s3_output_bucket_name}", bucket_name)
    
    print("User data script: ", user_data_script)

    # Create an EC2 instance with the downloaded user data script
    ec2_client = boto3.client('ec2')
    
    try:
        
        instance = ec2_client.run_instances(
            ImageId=ami_id,  
            InstanceType=instance_type,  
            KeyName=key_name,  
            MinCount=1,
            MaxCount=1,
            UserData= user_data_script,      # User data script
            IamInstanceProfile={
                'Name': 'EC2S3AccessRole'
                },
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': id}]
                    
                }]
        )
    except Exception as e:
        print(f"Error Instantiating Ec2: {e}")
        return None

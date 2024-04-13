import json
import boto3
from botocore.exceptions import ClientError

# Initialize the S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    # Parse the incoming JSON payload
    body = json.loads(event['body'])
    fileName = body['fileName']
    contentType = body['contentType']

    # Parameters for generating the signed URL
    params = {
        'Bucket': 'pocprojectbucket',
        'Key': fileName,
        'ContentType': contentType
    }
    
    try:
        
        # Generate the signed URL
        signed_url = s3.generate_presigned_url(ClientMethod='put_object', Params=params, ExpiresIn=300,HttpMethod='PUT')

        # Return the signed URL in the response
        return {
            'statusCode': 200,
            
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS, GET, POST, PUT, DELETE"
                
            },
            'body': json.dumps({'url': signed_url}),

        }

    except ClientError as e:
        # Output the error to the console
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

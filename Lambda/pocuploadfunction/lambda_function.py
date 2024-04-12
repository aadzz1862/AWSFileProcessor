# lambda_function.py
import boto3
import json
import nanoid

def lambda_handler(event, context):
    
    # Parse the incoming JSON data
    body = json.loads(event['body'])
    
    print("Received event:", body)
    
    # Save the data to DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('poctable')
    
    table.put_item(Item={

        'id': nanoid.generate(),
        'input_text': body['input_text'],
        'input_file_path': body['input_file_path']
    })
    
    
    return {
        'statusCode': 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",

            "Access-Control-Allow-Methods": "OPTIONS, GET, POST, PUT, DELETE"
        },
        'body': json.dumps('Data saved successfully.')
    }

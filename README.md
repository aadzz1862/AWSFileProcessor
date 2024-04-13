# AWS File Processor

This project demonstrates a full-stack application integrating a React front-end with various AWS services for backend processing. The workflow includes collecting user input text and file uploads through a React app, storing files in S3 logging metadata in DynamoDB, processing the data using Lambda and EC2 instances, append the input text into the input file, and finally uploading the output file into S3 while terminating the instance.

This React application allows users to upload text and .txt files directly to an AWS S3 bucket via a user-friendly web interface.

## Features

- Responsive UI built with ReactJS.
- Text input for user-entered data.
- File input for uploading .txt files.
- Direct file uploads to AWS S3 using pre-signed URLs for enhanced security.

## Directory Structure

```
/
├── Lambda/
│   ├── generatesignedurl/
│   │   ├── generatesignedurl.yaml
│   │   └── lambda_function.py
│   ├── pocprocessdynamodbinsert/
│   │   ├── pocprocessdynamodbinsert.yaml
│   │   └── lambda_function.py
│   └── pocuploadfunction/
│       ├── pocuploadfunction.yaml
│       └── lambda_function.py
├── Scripts/
│   └── user_data_script.sh
└── poc-react-app/
    ├── public/
    ├── src/
    ├── .gitignore
    ├── package-lock.json
    ├── package.json
    └── README.md

```

#### Lambda 
This folder contains source code for the three lambda fuctions used in this project. 

`generatesignedurl` : This Lambda function creates a signed URL to facilitate secure uploads of files to the S3 bucket, ensuring the uploaded files remain private.

`pocprocessdynamodbinsert` : This Lambda function activates upon the insertion of a record in the DynamoDB table, launching an EC2 instance to process the file that has been uploaded. A user data script, containing the logic for appending the input text, is executed by this EC2 instance, which the Lambda function supplies along with the required input parameters.

`pocuploadfunction` : The Lambda function serves the purpose of transmitting the file name and its corresponding S3 path to a DynamoDB table, where this information is recorded and stored.

#### Scripts 

This folder contains a user data script `user_data_script.sh` that is executed by an EC2 instance generated on-demand. The script is responsible for processing the file, retrieving file information from the DynamoDB table, and subsequently uploading the outcomes back to the DynamoDB table.

#### poc-react-app 

This folder contains cod for the frontend React.js application.


## Build and Deployment
This section details how to build and run the project:

### Dependencies: 

- Node.js (LTS version)
- npm (typically installed with Node.js)
- An AWS account
- AWS CLI installed and configured

This project is tested on the below software configurations

`NodeJS v21.7.3, NPM 10.5.2, react-js 17.0.2, aws-cli 2.15.37 Python 3.11.9`

`Python 3.10, nanoid 2.0.0 for lambda functions`


### Build Instructions: 

#### AWS Setup

##### S3 Buckets

I'm using two s3 buckets on this application

1. Create an S3 bucket called `pocprojectbucket` via the AWS Management Console. This bucket is used to upload the input files,  process files and user data script file for EC2. We are using only one bucket for all purpose and this bucket is made not accessible to public.

<img width="1300" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/7a2c0570-3704-4cdb-aead-448f57698f5b">



Cross-origin resource sharing (CORS) for this bucket

```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "PUT",
            "GET"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": []
    }
]
```
   

2. Another s3 bucket called 'fileprocessorapp' is used to host the react-js applciation. This bucket is publically accessible.

   <img width="1318" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/dbdc23fc-8a4a-40a1-a852-170680524b18">


Static Website Hosting 

<img width="1347" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/bd840ee6-fbfb-4490-80ac-dd5acadf8337">


Bucket Policy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::fileprocessorapp/*"
        }
    ]
}

```

#### AWS Systems Manager Parameter Store

AWS Systems Manager Parameter Store is used stored the configurations for lambda. This prevent hardcoding the parameter values in the code.

<img width="1048" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/42c8d5e7-6487-4d61-86b1-3bbc68b33daa">

<img width="1037" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/c774790d-f00d-4290-af15-225a9cca76c3">

##### AWS Lambda

The coniguration of Lambdas used in this applcition is as below.

generatesignedurl

This lambda is for generating the signed url for s3 bucket with a short expiry time so the s3 bucket is not exposed to public and the applciation get only momentary access to upload the file using the signed url. this make the S3 bucket highly secure.

<img width="795" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/2dcef3e1-8391-4e6f-a364-0102795c0dcf">

Create the lambda using the pyhton code from `Lambda/generatesignedurl/lambda_function.py`

Detailed configuration for this lamba is availbe on the yaml file `generatesignedurl.yaml`

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::pocprojectbucket/*",
    }
  ]
}

```

pocprocessdynamodbinsert

This lambda is to create a new VM automatically and triggered when a new record is inserted into DynamoDb table `poctable`

<img width="769" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/a81a012d-67c4-4048-875c-37b69d01a78c">


Create the lambda using the pyhton code from `Lambda/pocprocessdynamodbinsert/lambda_function.py`

Detailed configuration for this lamba is availbe on the yaml file `pocprocessdynamodbinsert.yaml`

Add the below permisssion for this lamda roles in IAM

<img width="817" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/81a6f957-dc0a-4357-9843-766724edac84">

dynamodbreadstream 

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"dynamodb:GetRecords",
				"dynamodb:GetShardIterator",
				"dynamodb:DescribeStream",
				"dynamodb:ListStreams"
			],
			"Resource": "arn:aws:dynamodb:us-east-2:730335433926:table/poctable/stream/2024-04-12T14:40:41.878"
		}
	]
}

```

EC2InstancePassRolePolicy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::730335433926:role/EC2S3AccessRole",
            "Condition": {
                "StringEquals": {
                    "iam:PassedToService": "ec2.amazonaws.com"
                }
            }
        }
    ]
}
```

pocuploadfunction

This lambda is to store the fiename and and s3 file path to the DynamoDB table `poctable`

<img width="803" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/28dcaa70-7af4-4953-9786-a18f5c23db76">


Create the lambda using the pyhton code from `Lambda/pocuploadfunction/lambda_function.py`

Detailed configuration for this lamba is availbe on the yaml file `pocuploadfunction.yaml`

This lambda have a layer created for the dependecy package for nanoid 2.0.0 python package

<img width="1580" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/2ebd7657-0935-4a98-b6f7-cc4642705c35">

Add the below permisssion for this lamda roles in IAM

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": "dynamodb:PutItem",
			"Resource": "arn:aws:dynamodb:us-east-2:730335433926:table/poctable"
		}
	]
}
```

##### DynamoDB

1. Create a DynamoDB table named `poctable`
2. For the Partition key, enter `id` and select the type as `String`. This will be the unique identifier for each record.
3. Click "Create" to provision the new table.
    - Note: The actual `id` values will be generated by the Lambda function using the `nanoid` library when new records are inserted, ensuring each entry is unique.

Setup DynamoDB event
Enable DynamoDB Streams on DyanamoDB table `poctable`
<img width="600" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/5876e779-7fb0-410a-8ef6-497f183a003d">

Create an IAM Role Policy for AWS Lambda pocprocessdynamodbinsert
<img width="600" alt="image" src="https://github.com/aadzz1862/AWSFileProcessor/assets/86231542/7d5ec9cb-fe8e-4c55-a66f-14ea57fa7a4b">


##### API Gateway



### Run Instructions: 

Explain how to run the project locally.

## Setup

To get this project running on your local machine, follow these detailed steps.

### Prerequisites

You will need:

- Node.js (LTS version)
- npm (typically installed with Node.js)
- An AWS account
- AWS CLI installed and configured


### 1. AWS Configuration

#### S3 Bucket

1. Create an S3 bucket via the AWS Management Console.
2. Update the bucket policy to allow public reads and set up CORS (given below) to allow requests from your domain.
```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "PUT",
            "POST",
            "GET"
        ],
        "AllowedOrigins": [
            "http://localhost:3000"
        ],
        "ExposeHeaders": []
    }
]
```

#### Cognito Identity Pool

1. Create a new identity pool in AWS Cognito.
2. Enable access to unauthenticated identities.
3. Associate the identity pool with an IAM role (If you don't have any create a new one with the name you like).
4. Make sure that this IAM role have permission to put objects in your S3 bucket.

#### DynamoDB
1. Create a DynamoDB table named `poctable`
2. For the Partition key, enter `id` and select the type as `String`. This will be the unique identifier for each record.
3. Click "Create" to provision the new table.
    - Note: The actual `id` values will be generated by the Lambda function using the `nanoid` library when new records are inserted, ensuring each entry is unique.

#### Lambda Function

1. Create a Lambda function in AWS.
2. Use the provided in `lambda_function.py` (/Lambda/pocuploadfunction/) as the code base.
3. Assign an execution role for this Lambda Function that has permissions to write to DynamoDB and S3.
4. Also, create another Lambda Function and use the code (/Lambda/pocprocessdynamodbinsert/) as the code base.
5. Assign an execution role for this Lambda Function that has permissions to write to DynamoDB and S3.

#### API Gateway

1. Set up an API Gateway to trigger the Lambda function.
2. Create a REST and POST method connected to the Lambda.
3. The CORS configuration required for Api is code inside Lambda Function, so no worries on that here.



### 2. Local Project Setup

1. Clone the project repository:

```
sh
git clone https://github.com/your-username/react-s3-uploader.git
cd react-s3-uploader/poc-react-app
```
2. Update npm package using the below command.

```
npm update
```
3. To start the application, run the below command.
```
npm start
```


## Deployment Flow

- Users upload files and input data via the React app. This information is then uploaded to S3, and corresponding metadata is logged to DynamoDB.
- The upload to S3 triggers Lambda function to log file metadata in DynamoDB.
- The insert into DynamoDB triggers the second Lambda function to run the script stored in S3, which then initiate EC2 instances for further processing.

## Troubleshooting & Logging

- AWS CloudWatch: Essential for monitoring Lambda executions, EC2 instance status, and debugging issues.
- IAM Roles: Ensure all AWS services (Lambda, EC2, S3, DynamoDB) have roles with appropriate permissions.
- React Developer Tools: Useful for debugging front-end issues.


## BONUS

### `S3 Web Hosting`

The frontend code is deployed to S3 as a static website. 
http://fileprocessorapp.s3-website.us-east-2.amazonaws.com


## References

1. [Configuring CORS in AWS using the S3 Console](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enabling-cors-examples.html)
2. [Building REST API](https://docs.aws.amazon.com/apigateway/latest/developerguide/getting-started-aws-proxy.html)
3. [Enabling CORS by API console](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors-console.html)
4. [nanoid id, read the full docs if you don't have prior experience](https://www.npmjs.com/package/nanoid)
5. [Building lambda with Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
6. [Hosting a static website using Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)

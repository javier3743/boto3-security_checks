# Secutity checks using boto3 
Using Boto3, pytest and moto for creating and testing scripts that checks for some vulnerabilities in aws services

## Available scripts 

- remove_ssm_policy: Check if the EC2 account instances have assigned the SSM policy on their roles, if that is the case remove that policy from all instances.
- check_rds_public_access: Check if the RDS Instances have public access, if that is the case remove it to avoid undesired access.
- check_s3_public_access: Check if the s3 buckets have public access, if that is the case remove it to avoid undesired access.

## Prerequisites:

- Pyhton 3.x
- Pip
- AWS CLI

## How to use

1. Install the required libraries (boto3, pytes and moto).
```
pip install boto3 pytest moto
```
2. Ensure your AWS credentials are configured properly (do not recommend this way of setting your credentials but is the easiest for a test).
```
aws configure
```
3. Select the script you like to execute (remove_ssm_policy, check_rds_public_access, check_s3_public_access)
```
python remove_ssm_policy.py
```

To run the tests the unit test:
```
pytest 
```

import boto3
import json
from botocore.exceptions import ClientError


def list_buckets():
    """List all S3 buckets."""
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]


def is_bucket_public(bucket_name):
    """Check if the bucket has public access."""
    s3 = boto3.client('s3')
    try:
        # Check bucket ACL
        acl = s3.get_bucket_acl(Bucket=bucket_name)
        for grant in acl['Grants']:
            if 'URI' in grant['Grantee'] and 'AllUsers' in grant['Grantee']['URI']:
                return True

        # Check bucket policy
        policy = s3.get_bucket_policy(Bucket=bucket_name)
        policy_json = json.loads(policy['Policy'])
        for statement in policy_json['Statement']:
            if (statement['Effect'] == 'Allow' and 
                'Principal' in statement and 
                statement['Principal'] == '*'):
                return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            pass
        else:
            raise
    return False


def remove_public_access(bucket_name):
    """Remove public access from the bucket."""
    s3 = boto3.client('s3')
    try:
        # Update bucket ACL
        acl = s3.get_bucket_acl(Bucket=bucket_name)
        public_grantee_uri = 'http://acs.amazonaws.com/groups/global/AllUsers'
        new_grants = [
            grant for grant in acl['Grants']
            if grant.get('Grantee', {}).get('URI') != public_grantee_uri
        ]
        s3.put_bucket_acl(
            Bucket=bucket_name,
            AccessControlPolicy={
                'Grants': new_grants,
                'Owner': acl['Owner']
            }
        )

        # Delete bucket policy
        s3.delete_bucket_policy(Bucket=bucket_name)
        print(f'Removed public access from bucket: {bucket_name}')
    except ClientError as e:
        print(f'Error removing public access from bucket {bucket_name}: {e}')


def main():
    """Main function to check and remove public access from all buckets."""
    buckets = list_buckets()
    for bucket in buckets:
        if is_bucket_public(bucket):
            remove_public_access(bucket)
        else:
            print(f'Bucket {bucket} does not have public access.')


if __name__ == '__main__':
    main()

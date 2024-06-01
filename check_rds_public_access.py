import boto3
from botocore.exceptions import ClientError


def get_rds_instances():
    """List all RDS instances."""
    rds = boto3.client('rds')
    try:
        response = rds.describe_db_instances()
        return response['DBInstances']
    except ClientError as e:
        print(f"Error retrieving RDS instances: {e}")
        return []


def check_and_remove_public_access(instance):
    """Check if an RDS instance has public access and remove it if true."""
    rds = boto3.client('rds')
    instance_id = instance['DBInstanceIdentifier']
    
    if instance['PubliclyAccessible']:
        try:
            rds.modify_db_instance(
                DBInstanceIdentifier=instance_id,
                PubliclyAccessible=False,
                ApplyImmediately=True
            )
            print(f"Public access removed from instance {instance_id}")
        except ClientError as e:
            print(f"Error modifying RDS instance {instance_id}: {e}")
    else:
        print(f"Instance {instance_id} does not have public access")


def main():
    """Main function to check and remove public access from all RDS instances."""
    instances = get_rds_instances()
    for instance in instances:
        check_and_remove_public_access(instance)


if __name__ == "__main__":
    main()

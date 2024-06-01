import boto3


def list_instances():
    """List all EC2 instances."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return instances


def get_instance_iam_role(instance_id):
    """Get the IAM role of an EC2 instance."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_iam_instance_profile_associations(
        Filters=[
            {'Name': 'instance-id', 'Values': [instance_id]}
        ]
    )
    if response['IamInstanceProfileAssociations']:
        return response['IamInstanceProfileAssociations'][0][
            'IamInstanceProfile'
        ]['Arn']
    return None


def remove_ssm_policy_from_role(role_name):
    """Remove SSM policy from the IAM role."""
    iam = boto3.client('iam')
    policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    try:
        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    except iam.exceptions.NoSuchEntityException:
        pass


def main():
    """Main function to remove SSM policy from roles of all EC2 instances."""
    instances = list_instances()
    for instance_id in instances:
        role_arn = get_instance_iam_role(instance_id)
        if role_arn:
            role_name = role_arn.split('/')[-1]
            remove_ssm_policy_from_role(role_name)


if __name__ == "__main__":
    main()

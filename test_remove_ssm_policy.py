import boto3
import pytest
from moto import mock_aws
import remove_ssm_policy as ec2_check


@pytest.fixture
def setup_ec2():
    """Setup EC2 instance for testing."""
    with mock_aws():
        ec2 = boto3.client('ec2')
        ec2.run_instances(
            ImageId='ami-12345678', 
            MinCount=1, 
            MaxCount=1, 
            InstanceType='t2.micro'
        )
        yield


@pytest.fixture
def setup_iam():
    """Setup IAM for testing."""
    with mock_aws():
        iam = boto3.client('iam')
        role_name = 'test-role'
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=(
                '{"Version":"2012-10-17","Statement":[{"Effect":"Allow",'
                '"Principal":{"Service":"ec2.amazonaws.com"},'
                '"Action":"sts:AssumeRole"}]}'
            )
        )
        iam.create_instance_profile(InstanceProfileName=role_name)
        iam.add_role_to_instance_profile(InstanceProfileName=role_name, RoleName=role_name)
        yield


def test_list_instances(setup_ec2):
    """Test listing all EC2 instances."""
    instances = ec2_check.list_instances()
    assert len(instances) == 1


def test_get_instance_iam_role(setup_ec2, setup_iam):
    """Test getting the IAM role of an EC2 instance."""
    ec2 = boto3.client('ec2')
    instance_id = ec2.describe_instances()['Reservations'][0]['Instances'][0]['InstanceId']
    ec2.associate_iam_instance_profile(
        IamInstanceProfile={
            'Arn': 'arn:aws:iam::123456789012:instance-profile/test-role', 
            'Name': 'test-role'
        },
        InstanceId=instance_id
    )
    role_arn = ec2_check.get_instance_iam_role(instance_id)
    assert role_arn == 'arn:aws:iam::123456789012:instance-profile/test-role'


def test_remove_ssm_policy_from_role(setup_iam):
    """Test removing SSM policy from the IAM role."""
    iam = boto3.client('iam')
    role_name = 'test-role'
    ec2_check.remove_ssm_policy_from_role(role_name)
    attached_policies = iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
    assert all(
        policy['PolicyArn'] != "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore" 
        for policy in attached_policies
    )


if __name__ == '__main__':
    pytest.main()

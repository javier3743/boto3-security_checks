import pytest
import boto3
from moto import mock_aws
import check_rds_public_access as rds_check


@pytest.fixture
def rds_instance_public():
    """Setup a public RDS instance fixture."""
    return {
        'DBInstanceIdentifier': 'test-instance-public',
        'PubliclyAccessible': True
    }


@pytest.fixture
def rds_instance_private():
    """Setup a private RDS instance fixture."""
    return {
        'DBInstanceIdentifier': 'test-instance-private',
        'PubliclyAccessible': False
    }


@pytest.fixture
def rds_client():
    """Setup the mock AWS RDS client."""
    with mock_aws():
        client = boto3.client('rds')
        yield client


@pytest.fixture
def create_rds_instances(rds_client):
    """Setup the RDS instances."""
    def _create_instance(instance_id, publicly_accessible):
        rds_client.create_db_instance(
            DBInstanceIdentifier=instance_id,
            DBInstanceClass='db.t2.micro',
            Engine='mysql',
            AllocatedStorage=20,
            MasterUsername='username',
            MasterUserPassword='password',
            PubliclyAccessible=publicly_accessible
        )
    return _create_instance


def test_get_rds_instances(rds_client, create_rds_instances):
    """Test listing all RDS instances."""
    create_rds_instances('test-instance', True)

    instances = rds_check.get_rds_instances()
    assert len(instances) == 1
    assert instances[0]['DBInstanceIdentifier'] == 'test-instance'


def test_check_and_remove_public_access_public_instance(
    rds_client, rds_instance_public, create_rds_instances
):
    """Test checking and removing public access for a public instance."""
    create_rds_instances(
        rds_instance_public['DBInstanceIdentifier'],
        rds_instance_public['PubliclyAccessible']
    )

    rds_check.check_and_remove_public_access(rds_instance_public)

    response = rds_client.describe_db_instances(
        DBInstanceIdentifier='test-instance-public'
    )
    assert response['DBInstances'][0]['PubliclyAccessible'] is False


def test_check_and_remove_public_access_private_instance(
    rds_client, rds_instance_private, create_rds_instances
):
    """Test checking and removing public access for a private instance."""
    create_rds_instances(
        rds_instance_private['DBInstanceIdentifier'],
        rds_instance_private['PubliclyAccessible']
    )

    rds_check.check_and_remove_public_access(rds_instance_private)

    response = rds_client.describe_db_instances(
        DBInstanceIdentifier='test-instance-private'
    )
    assert response['DBInstances'][0]['PubliclyAccessible'] is False


if __name__ == '__main__':
    pytest.main()

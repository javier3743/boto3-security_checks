import boto3
from botocore.exceptions import ClientError
import pytest
from moto import mock_aws
import check_s3_public_access as s3_check


@pytest.fixture
def s3_setup():
    """Set up a mock AWS environment for testing."""
    with mock_aws():
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket='test-bucket')
        s3.put_bucket_acl(Bucket='test-bucket', ACL='public-read')
        yield s3


def test_list_buckets(s3_setup):
    """Test listing all buckets."""
    buckets = s3_check.list_buckets()
    assert 'test-bucket' in buckets


def test_is_bucket_public(s3_setup):
    """Test checking if a bucket has public access."""
    assert s3_check.is_bucket_public('test-bucket')

    s3_setup.put_bucket_acl(Bucket='test-bucket', ACL='private')
    assert not s3_check.is_bucket_public('test-bucket')


def test_remove_public_access(s3_setup):
    """Test removing public access from a bucket."""
    s3_setup.put_bucket_acl(Bucket='test-bucket', ACL='public-read')
    s3_check.remove_public_access('test-bucket')
    assert not s3_check.is_bucket_public('test-bucket')


if __name__ == '__main__':
    pytest.main()

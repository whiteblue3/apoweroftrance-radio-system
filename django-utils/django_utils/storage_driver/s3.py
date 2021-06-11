"""
S3 업로드
"""
import boto3
from botocore.exceptions import ClientError
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


bucket = settings.AWS_STORAGE_BUCKET_NAME
location = settings.MEDIAFILES_LOCATION

s3 = boto3.client('s3')

"""S3 가속 서비스를 사용하는 경우"""
# region = settings.AWS_S3_REGION_NAME
# session = Session(region_name=region,
#                   aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
# s3 = session.client('s3')
# s3.get_bucket_acl(Bucket=bucket)
# s3.put_bucket_accelerate_configuration(Bucket=bucket, AccelerateConfiguration={'Status': 'Enabled'})


def upload_data(data, remote_path, remote_file_name, mimetype, filesize):
    remote_file_path = '%s/%s/%s' % (location, remote_path, remote_file_name)
    try:
        s3.put_object(
            Body=data.read(),
            ContentLength=filesize,
            Bucket=bucket,
            Key=remote_file_path,
            ACL='public-read',
            ContentType=mimetype)
    except ClientError as e:
        logger.exception("Upload file data to S3 Error {}".format(e))
        raise e
    else:
        return remote_file_path


def delete_file(path, file_name):
    try:
        s3.delete_object(Bucket=bucket, Key='%s/%s/%s' % (location, path, file_name))
    except ClientError as e:
        logger.exception("Delete file from S3 Error {}".format(e))
        raise e


def read_file(path, file_name):
    try:
        result = s3.get_object(Bucket=bucket, Key='%s/%s/%s' % (location, path, file_name))
    except ClientError as e:
        logger.exception("Read file from S3 Error {}".format(e))
        raise e
    else:
        return result['Body'].read()


def exist_file(path, file_name):
    file = read_file(path, file_name)
    if file is not None:
        return True
    else:
        return False

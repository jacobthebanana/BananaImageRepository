import boto3
from bananaImageRepository.settings import S3_HOSTNAME, S3_BUCKETNAME, S3_ACCESS_KEY, S3_SECRET_KEY, S3_ENDPOINT_URL

def getS3Client():
    session = boto3.session.Session()
    
    s3_client = session.client(
        service_name="s3",
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        endpoint_url=S3_ENDPOINT_URL,
    )

    return s3_client

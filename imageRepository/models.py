from django.db import models
from bananaImageRepository.settings import S3_HOSTNAME, S3_BUCKETNAME, S3_ACCESS_KEY, S3_SECRET_KEY, S3_ENDPOINT_URL

import io
import boto3
import uuid

class Image(models.Model):
    # The Django developers recommends not to override the __init__
    # method of modes.
    def initialize(self, name, imageFileBytes, imageFileSize):        
        session = boto3.session.Session()
        s3_client = session.client(
            service_name="s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            endpoint_url=S3_ENDPOINT_URL,
        )

        self.fileName = name
        self.s3ObjectUUID = uuid.uuid4()
        self.size = imageFileSize

        s3_client.put_object(
            Bucket=S3_BUCKETNAME, 
            Key=f"{str(self.s3ObjectUUID)}-{self.fileName}", 
            Body=imageFileBytes,  
        )


    # Filenames could be as long as what s3 supports.
    fileName = models.CharField(max_length=255, verbose_name="File name")
    s3ObjectUUID = models.UUIDField()
    size = models.BigIntegerField(verbose_name="File Size (bytes)")

    md5 = models.CharField(max_length=32, verbose_name="Image File MD5")

    labels = models.ManyToManyField("Label")


    
class Label(models.Model):
    name = models.CharField(max_length=255, verbose_name="Label name")
    imageNetID = models.IntegerField(verbose_name="category ID in dataset, starting from 0.")
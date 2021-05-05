from django.db import models
import datetime

from bananaImageRepository.settings import S3_HOSTNAME, S3_BUCKETNAME, S3_ACCESS_KEY, S3_SECRET_KEY, S3_ENDPOINT_URL
from s3.s3_utils import getS3Client

import io
import boto3
import uuid

class Image(models.Model):
    # The Django developers recommends not to override the __init__
    # method of modes.
    def upload(self, imageFileBytes):     
        s3_client = getS3Client()   
        s3_client.put_object(
            Bucket=S3_BUCKETNAME, 
            Key=self.fileName, 
            Body=imageFileBytes,  
        )

    def getURL(self, validFor=3600):
        """
        Get presigned URL for accessing this s3 object.
        `validFor` is measured in seconds.
        """
        s3_client = getS3Client()
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKETNAME,
                'Key': self.fileName,
            },
            ExpiresIn=validFor,
        )

        return url

    def delete(self, *args, **kwargs):
        s3_client = getS3Client()
        s3_client.delete_object(
            Bucket=S3_BUCKETNAME,
            Key=self.fileName,
        )
        
        for label in self.labels.all():
            if len(label.image_set.all()) <= 1:
                label.delete()
        
        super().delete(*args, **kwargs)


    @property
    def allLabels(self) -> str:
        names = []
        for label in self.labels.all():
            names.append(label.name)
        
        return ", ".join(names)

    # Filenames could be as long as what s3 supports.
    fileName = models.CharField(max_length=255, verbose_name="File name")
    size = models.BigIntegerField(verbose_name="File Size (bytes)")
    md5 = models.CharField(max_length=32, verbose_name="Image File MD5")

    attribution = models.CharField(max_length=1000, verbose_name="Image attribution")

    labels = models.ManyToManyField("Label")

    
class Label(models.Model):
    name = models.CharField(max_length=255, verbose_name="Label name")
    imageNetID = models.IntegerField(verbose_name="category ID in dataset, starting from 0.")
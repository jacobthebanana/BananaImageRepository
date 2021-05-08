from django.db import models
import datetime

from bananaImageRepository.settings import S3_PUBLIC_URL, S3_BUCKETNAME
from s3.s3_utils import getS3Client

import io
import boto3
import uuid

from urllib.parse import urlparse

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

        The browser-accessible public URL (e.g., http://localhost:9000/something)
        might be distinct from the endpoint URL 
        (e.g., http://172.16.0.3/something, internal to the Docker network.)
        """
        s3_client = getS3Client()
        
        originalPresignedS3Url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKETNAME,
                'Key': self.fileName,
            },
            ExpiresIn=validFor,
        )

        parsedUrl = urlparse(originalPresignedS3Url)
        
        return S3_PUBLIC_URL + parsedUrl.path + "?" + parsedUrl.query

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
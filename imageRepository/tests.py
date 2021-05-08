from django.test import TestCase
import datetime
import requests

from bananaImageRepository.settings import S3_BUCKETNAME
from imageRepository.models import Image, Label

import os
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile



TEST_IMAGE_URL = os.environ.get("TEST_IMAGE_URL")
TEST_IMAGE_PATH = os.environ.get("TEST_IMAGE_PATH")

if (not TEST_IMAGE_URL) and (not TEST_IMAGE_PATH):
    print(
        """
        Please specify at least one of the following env variables:
        - TEST_IMAGE_URL (for fetching the test image from the internet,) or 
        - TEST_IMAGE_PATH (for a local test image, in case the test server is airgapped.)
        """
    )

    raise 

else:
    if not TEST_IMAGE_PATH:
        TEST_IMAGE_PATH = "/dev/shm/testImage.jpg"

    if TEST_IMAGE_URL:
        testImageBytes = requests.get(TEST_IMAGE_URL).content
        with open(TEST_IMAGE_PATH, "wb") as testImageFile:
            testImageFile.write(testImageBytes)


def deleteAllImages():
    images = Image.objects.all()
    for image in images:
        image.delete()


class LabelingIntegrationTestCase(TestCase):
    def setUp(self):
        pass
    
    def test_labeling(self):
        """
        Verify that the labelling API call is successful. 
        """
        with open(TEST_IMAGE_PATH, "rb") as testImage:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                response = self.client.post(
                    '/add_image/',
                    data={"imageFile": testImage},
                    format='multipart',
                )
            
                self.assertEqual(response.status_code, 200)

    def tearDown(self):
        deleteAllImages()


class S3IntegrationTestCase(TestCase):
    def setUp(self):
        with open(TEST_IMAGE_PATH, "rb") as testImage:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                    imageUploadRequest = self.client.post(
                        '/add_image/',
                        data={"imageFile": testImage},
                        format='multipart',
                    )

                    self.assertEqual(imageUploadRequest.status_code, 200)
                
        self.testImageObject = Image.objects.last()

    def test_presigned_url_image_matches(self):
        """
        Verify that the image presented to visitors (via the presigned S3 URL) is correct.
        """
        imageRedirectionResponse = self.client.get(
            f"/get_image_url/{self.testImageObject.id}",
            follow=False,
        )

        # S3 presigned URLs are euphermal. Use temporary 302 redirect rather than 301.
        self.assertEqual(imageRedirectionResponse.status_code, 302)  
        
        actualImageURL = imageRedirectionResponse.headers["Location"]

        # This call goes to the S3 server (not Django.) 
        # Hence the GET call uses Python's requests 
        # rather than the Django unit test client.
        s3ImageResponse = requests.get(actualImageURL)
        self.assertEqual(testImageBytes, s3ImageResponse.content)
        
    def tearDown(self):
        self.testImageObject.delete()


class ImageTestCase(TestCase):
    def setUp(self):
        pass

    def test_duplicate_image(self):
        """
        Verify that the add-image view rejects duplicate image uploads.
        """
        with open(TEST_IMAGE_PATH, "rb") as testImage:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                legitimateRequest = self.client.post(
                    '/add_image/',
                    data={"imageFile": testImage},
                    format='multipart',
                )

                self.assertEqual(legitimateRequest.status_code, 200)

                responseToDuplicate = self.client.post(
                    '/add_image/',
                    data={"imageFile": testImage},
                    format='multipart',
                )

                self.assertGreaterEqual(responseToDuplicate.status_code, 400)
        
    def tearDown(self):
        deleteAllImages()


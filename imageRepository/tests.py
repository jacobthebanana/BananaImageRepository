from django.test import TestCase
import datetime

from imageRepository.models import Image, Label


class ImageTestCase(TestCase):
    def setUp(self):
        self.testImage1 = Image.objects.create(
            fileName=(
                    datetime.datetime.now().strftime("%Y-%m-%d-_%H-%M-%S") + "-_" +
                    "testImage1.jpg"
                ),
            size=10000,
            md5="0123456789abcdef0123456789abcdef",
            attribution="Public Domain",
        )

    def test_duplicate_image(self):
        self.testImage1
        
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.post(
                '/add_image',
                data=b"image-file"
            )
        
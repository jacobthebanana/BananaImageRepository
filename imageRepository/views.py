from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.core.exceptions import SuspiciousOperation

import base64
import hashlib
import requests

from imageRepository.forms import ImageUploadForm
from imageRepository.models import Image, Label
from bananaImageRepository.settings import IMAGE_CLASSIFICATION_API_URL, IMAGE_CLASSIFICATION_LABELS


def uploadView(request):
    if request.method == "GET":
        form = ImageUploadForm()
        return render(request, 'add_image/add_image.html', {'form': form})
    
    elif request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            imageFile = request.FILES["imageFile"]
            imageFileName = imageFile.name
            imageFileBytes = imageFile.file.read()
            imageFileSize = imageFile.size

            md5 = str(hashlib.md5(imageFileBytes))

            if Image.objects.filter(md5=md5):
                raise SuspiciousOperation("This image file already exists in the database.")

            encodedImage = base64.b64encode(imageFileBytes).decode('utf-8')
            
            response = requests.post(
                IMAGE_CLASSIFICATION_API_URL, 
                data='{"instances" : [{"b64": "%s"}]}' % encodedImage
            )

            prediction = response.json()['predictions'][0]['classes']
            prediction_label_key = str(int(prediction) - 1)
            labels = IMAGE_CLASSIFICATION_LABELS[prediction_label_key].split()

            image = Image()
            image.initialize(
                name=imageFileName,
                imageFileBytes=imageFileBytes,
                imageFileSize=imageFileSize,
            )

            image.save()

            for label_name in labels:
                # Try finding this label. It might not exist in database yet.
                label_object_matches = Label.objects.filter(name=label_name)

                if not label_object_matches:
                    label_object = Label(name=label_name, imageNetID=prediction_label_key)
                    label_object.save()
                else:
                    label_object = label_object_matches.first()

                print(image)
                image.labels.add(label_object) 

            image.save()

            return HttpResponse(labels)


def uploadConfirmationView(request):
    return HttpResponse("Upload confirmation placeholder.")

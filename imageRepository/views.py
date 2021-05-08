from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.core.exceptions import SuspiciousOperation

import datetime

import base64
import hashlib
import requests

from imageRepository.forms import ImageUploadForm
from imageRepository.models import Image, Label
from bananaImageRepository.settings import IMAGE_CLASSIFICATION_API_URL, IMAGE_CLASSIFICATION_LABELS


def uploadView(request):
    if request.method == "GET":
        form = ImageUploadForm()
        return render(request, 'add_image/add_image.html', getRenderContext(context={'form': form}))
    
    elif request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            imageFile = request.FILES["imageFile"]
            imageFileName = imageFile.name
            imageFileBytes = imageFile.file.read()
            imageFileSize = imageFile.size

            md5 = hashlib.md5(imageFileBytes).hexdigest()

            if Image.objects.filter(md5=md5):
                raise SuspiciousOperation("This image file already exists in the database.")

            encodedImage = base64.b64encode(imageFileBytes).decode('utf-8')
            
            response = requests.post(
                IMAGE_CLASSIFICATION_API_URL, 
                data='{"instances" : [{"b64": "%s"}]}' % encodedImage
            )

            if response.status_code != 200:
                raise SuspiciousOperation("The image classification API returned a non-200 response code.")

            prediction = response.json()['predictions'][0]['classes']
            prediction_label_key = str(int(prediction) - 1)
            labels = IMAGE_CLASSIFICATION_LABELS[prediction_label_key].split(", ")

            image = Image.objects.create(
                fileName=(
                    datetime.datetime.now().strftime("%Y-%m-%d-_%H-%M-%S") + "-_" +
                    imageFileName
                ),
                size=imageFileSize,
                md5=md5,
                attribution=form.cleaned_data["attribution"]
            )

            try: 
                image.upload(imageFileBytes)
            except Exception as e:
                image.delete()
                raise e
            
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

            context = {
                "image": image,
            }

            return render(request, "add_image/add_image_success.html", getRenderContext(context=context))
        
        else:
            raise SuspiciousOperation("Invalid POST request.")


def allImagesView(request, labelID=None):
    if not labelID:
        images = Image.objects.all()
        label = None
    else:
        label = get_object_or_404(Label, id=labelID)
        images = Image.objects.filter(labels__in=[label])

    renderContext = {
        "label": label,
        "images": images,
    }
    return render(request, "list_images/list_images.html", getRenderContext(context=renderContext))


def getImageURL(request, imageID: int):
    """
    Speed up loading of elements other than images.  
    """
    image = get_object_or_404(Image, id=imageID)
    return redirect(image.getURL())


def getRenderContext(context={}):
    context["labels"] = Label.objects.all().order_by('name')
    return context
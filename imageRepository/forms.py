from django import forms

class ImageUploadForm(forms.Form):
    imageFile = forms.ImageField(required=True)

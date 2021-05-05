from django import forms

class ImageUploadForm(forms.Form):
    imageFile = forms.ImageField(required=True)
    attribution = forms.CharField(max_length=1000, required=False)
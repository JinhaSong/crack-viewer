from django import forms
from .models import ImageModel
from .models import SegGTModel

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields = ['image']

class SegGTUploadForm(forms.ModelForm):
    class Meta:
        model = SegGTModel
        fields = ['seg_image']
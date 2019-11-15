from django import forms
from .models import ImageModel

class ImageGTUploadForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields = ['image', 'seg_gt_image']


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields = ['image']

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from CrackViewer.utils import filename

class ImageModel(models.Model):
    image = models.ImageField(upload_to=filename.default)
    token = models.AutoField(primary_key=True)
    cc_th = models.IntegerField(default=0)
    severity_th = models.IntegerField(default=0)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    # updated_date = models.DateTimeField(auto_now=True)

class ClsResultModel(models.Model):
    image = models.ForeignKey(ImageModel, related_name='cls_results', on_delete=models.CASCADE)
    label = models.TextField(null=True, unique=False)
    x = models.FloatField(null=True, unique=False)
    y = models.FloatField(null=True, unique=False)
    w = models.FloatField(null=True, unique=False)
    h = models.FloatField(null=True, unique=False)

class SegResultModel(models.Model):
    image = models.ForeignKey(ImageModel, related_name='seg_results', on_delete=models.CASCADE)
    seg_image = models.ImageField()
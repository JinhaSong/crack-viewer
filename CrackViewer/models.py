# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from CrackViewer.utils import filename
from django_mysql.models import JSONField


class ImageModel(models.Model):
    image = models.ImageField(upload_to=filename.default)
    seg_gt_image = models.ImageField(upload_to=filename.default, null=True)
    token = models.AutoField(primary_key=True)
    cc_th = models.IntegerField(default=0)
    severity_th = models.IntegerField(default=0)
    uploaded_date = models.DateTimeField(auto_now_add=True)

class ClsResultModel(models.Model):
    image = models.ForeignKey(ImageModel, related_name='crack_reulst', on_delete=models.CASCADE)
    label = models.TextField(null=True, unique=False)
    x = models.FloatField(null=True, unique=False)
    y = models.FloatField(null=True, unique=False)
    w = models.FloatField(null=True, unique=False)
    h = models.FloatField(null=True, unique=False)
    severity = JSONField(null=True)


class SegResultModel(models.Model):
    image = models.ForeignKey(ImageModel, related_name='seg_result', on_delete=models.CASCADE)
    seg_image = models.ImageField()
    seg_image_th = models.ImageField()

class SegGTModel(models.Model):
    image = models.ForeignKey(ImageModel, related_name='seg_gt', on_delete=models.CASCADE)
    seg_image = models.ImageField()
    tp_image = models.ImageField(null=True)
    fp_image = models.ImageField(null=True)
    fn_image = models.ImageField(null=True)

class RegionResultModel(models.Model):
    image = models.ForeignKey(ImageModel, related_name='region_result', on_delete=models.CASCADE)
    region_num = models.IntegerField(null=True, unique=False)
    region_type = models.TextField(null=True, unique=False)
    severity_results = JSONField(null=True)
    patching_results = JSONField(null=True)


class RegionPositionModel(models.Model):
    region_model = models.ForeignKey(RegionResultModel, related_name='region_positions', on_delete=models.CASCADE)
    label = models.TextField(null=True, unique=False)
    x = models.FloatField(null=True, unique=False)
    y = models.FloatField(null=True, unique=False)
    w = models.FloatField(null=True, unique=False)
    h = models.FloatField(null=True, unique=False)


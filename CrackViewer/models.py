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
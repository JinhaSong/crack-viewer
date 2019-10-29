# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import ImageModel
from .models import ClsResultModel
from .models import SegResultModel

admin.site.register(ImageModel)
admin.site.register(ClsResultModel)
admin.site.register(SegResultModel)

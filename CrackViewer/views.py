# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageUploadForm
from .models import ImageModel
from time import sleep

import json, ast

@csrf_exempt
def upload(request) :
    template_name = "upload.html"
    if request.method == "POST" :
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()
            return redirect('/imagelist/')
        else :
            return redirect('/imagelist/')
    else :
        template_name = "upload.html"
        return render(request, template_name)

def imagelist(request) :
    image_model = ImageModel.objects.all().order_by('-pk')[:10]

    return render(request, 'imagelist.html', {'images' : image_model})

def imagedetail(request, image_pk) :
    image = ImageModel.objects.filter(pk=image_pk)
    return render(request, 'imagedetail.html', {'image' : image[0]})
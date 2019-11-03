# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageUploadForm, SegGTUploadForm
from .models import ImageModel, ClsResultModel, SegResultModel, SegGTModel
from .utils.AnalysisRequest import AnalysisRequest
from CrackSite import settings

from PIL import Image
from io import BytesIO, StringIO
import json, os, base64

@csrf_exempt
def upload(request) :
    if request.method == "POST" :
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()

            # Read image path
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/' ,str(image.image))

            # Send analysis request to crack-bridge-site
            analysis_request = AnalysisRequest()
            b_image = analysis_request.load_binary_image(image_path)
            analysis_request.set_request_attr(url='http://mltwins.sogang.ac.kr:8000/analyzer/', image=b_image, modules='crack')
            response = json.loads((analysis_request.send_request_message().content).decode("utf-8"))['results'][0]['module_result']

            # Get classification result and segmentation result from response of crack-bridge-site
            cls_results = response['classification_result']
            seg_result = response['image']

            # Define model variables
            segResultModel = SegResultModel.objects.create(image=image)

            # Save classification result
            for result in cls_results:
                clsResultModel = ClsResultModel.objects.create(image=image)

                final_label = ''
                label_list = []
                label_names = ['crack', 'lane', 'patch', 'normal']
                for label in result['label'] :
                    if label['description'] in label_names :
                        label_list.append(label)
                labels = sorted(label_list, key=lambda label_list:(label_list['score']), reverse=True)
                final_label = labels[0]

                if labels[0]['description'] == 'crack':
                    label_list = []
                    detail_label_names = ['lc', 'tc', 'ac', 'detail_norm']
                    for label in result['label']:
                        if label['description'] in detail_label_names:
                            label_list.append(label)
                    labels = sorted(label_list, key=lambda label_list: (label_list['score']), reverse=True)
                    if labels[0]['description'] == 'detail_norm' :
                        final_label = 'normal'
                    else :
                        final_label = labels[0]

                clsResultModel.label = final_label['description']
                clsResultModel.x = result['position']['x']
                clsResultModel.y = result['position']['y']
                clsResultModel.w = result['position']['w']
                clsResultModel.h = result['position']['h']
                clsResultModel.save()

            # Save classification result
            seg_img_path = os.path.join(str(image.image).split(".")[0] + "_seg" + ".png")
            segResultModel.seg_image = ContentFile(base64.b64decode(seg_result), name=seg_img_path)
            segResultModel.save()

            return redirect('/imagelist/')
        else :
            return redirect('/imagelist/')
    else :
        template_name = "upload.html"
        return render(request, template_name)

def compare_seg(request, image_pk) :
    if request.method == "POST":
        form = SegGTUploadForm(request.POST, request.FILES)
        print("form", form)
        if form.is_valid():
            print("valid")
            seg_image = form.save(commit=False)
            seg_image.image = ImageModel.objects.get(pk=image_pk)
            seg_image.save()
            return redirect('/compare_seg/' + str(image_pk))

        else :
            print('invalid')
            return redirect('/compare_seg/' + str(image_pk))
    else:
        template_name = "compare_seg.html"

        seg_result = ImageModel.objects.get(pk=image_pk)
        seg_gt = SegGTModel.objects.filter(image=image_pk)
        is_seg_gt = None
        if len(seg_gt) > 0:
            is_seg_gt = True
        else:
            is_seg_gt = False
        return render(request, template_name, {'image_pk': image_pk, 'seg_result':seg_result, 'seg_gt': seg_gt, 'is_seg_gt':is_seg_gt})

def image_list(request) :
    image_model = ImageModel.objects.all().order_by('-pk')[:10]

    return render(request, 'imagelist.html', {'images' : image_model})

def image_detail(request, image_pk) :
    image = ImageModel.objects.filter(pk=image_pk)
    seg_result = SegResultModel.objects.filter(image=image_pk)
    seg_image_url = str(seg_result[0].seg_image)

    return render(request, 'imagedetail.html', {
                      'image': image[0],
                      'image_pk': image_pk,
                      'seg_result': seg_image_url,
                  })
@csrf_exempt
def get_cracks(request) :
    cracks = []
    if request.method == "POST" :
        cls_result = ClsResultModel.objects.filter(image__pk=request.POST['image_pk'])
        for crack in cls_result :
            dict_crack = {}
            dict_crack['label'] = crack.label
            dict_crack['x'] = crack.x
            dict_crack['y'] = crack.y
            dict_crack['w'] = crack.w
            dict_crack['h'] = crack.h
            cracks.append(dict_crack)
    return HttpResponse(json.dumps({"cracks": cracks}), 'application/json')

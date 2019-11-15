# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageGTUploadForm, ImageUploadForm
from .models import *
from .utils.AnalysisRequest import AnalysisRequest
from CrackSite import settings

from PIL import Image
from io import BytesIO, StringIO
import json, os, base64

@csrf_exempt
def upload(request) :
    if request.method == "POST" :
        form = ImageGTUploadForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            return redirect('/imagelist/')
        else :
            return redirect('/imagelist/')
    else :
        template_name = "upload.html"
        return render(request, template_name)

@csrf_exempt
def upload_without_gt(request) :
    if request.method == "POST" :
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('/imagelist/')
        else :
            return redirect('/imagelist/')


def image_list(request) :
    image_model = ImageModel.objects.all().order_by('-pk')[:10]

    return render(request, 'imagelist.html', {'images' : image_model})

def image_detail(request, image_pk) :
    image = ImageModel.objects.filter(pk=image_pk)
    seg_result = SegResultModel.objects.filter(image=image_pk)
    seg_gt = SegGTModel.objects.filter(image=image_pk)
    is_analyzed = False
    is_gt = False
    seg_image_url = ""
    if len(seg_result) > 0 :
        is_analyzed = True
        seg_image_url = str(seg_result[0].seg_image)
    if len(seg_gt) > 0 :
        is_gt = True


    return render(request, 'imagedetail.html', {
                    'image': image[0],
                    'image_pk': image_pk,
                    'seg_result': seg_image_url,
                    'seg_gt':seg_gt,
                    'is_analyzed': is_analyzed,
                    'is_gt': is_gt
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

@csrf_exempt
def get_regions(request) :
    regions = []
    if request.method == "POST" :
        region_result = RegionResultModel.objects.filter(image__pk=request.POST['image_pk'])
        for region in region_result :
            dict_region = {}
            dict_region['region_num'] = region.region_num
            dict_region['region_type'] = region.region_type
            dict_region['patchs'] = []
            dict_region['distress_width'] = region.distress_width
            dict_region['distress_height'] = region.distress_height
            dict_region['distress_area'] = region.distress_area
            dict_region['distress_serverity'] = region.distress_serverity
            patchs = RegionPositionModel.objects.filter(region_model=region)
            for patch in patchs:
                dict_patch = {}
                dict_patch['label'] = patch.label
                dict_patch['x'] = patch.x
                dict_patch['y'] = patch.y
                dict_patch['w'] = patch.w
                dict_patch['h'] = patch.h
                dict_region['patchs'].append(dict_patch)
            regions.append(dict_region)
    return HttpResponse(json.dumps({"regions": regions}), 'application/json')

@csrf_exempt
def analysis(request) :
    result = []
    if request.method == "POST" :
        image = ImageModel.objects.filter(pk=request.POST['image_pk'])[0]
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/', str(image.image))

        # Send analysis request to crack-bridge-site
        analysis_request = AnalysisRequest()
        b_image = analysis_request.load_binary_image(image_path)
        analysis_request.set_request_attr(
            url='http://mltwins.sogang.ac.kr:8000/analyzer/',
            image=b_image, modules='crack',
            patch_size=request.POST['patch_size'],
            region_connectivity=int(request.POST['region_connectivity']),
            region_noise_filter=int(request.POST['region_noise_filter']),
            severity_threshold=int(request.POST['severity_threshold']),
        )
        response = json.loads((analysis_request.send_request_message().content).decode("utf-8"))['results'][0]['module_result']

        # Get classification result and segmentation result from response of crack-bridge-site
        cls_result = response['cls_result']
        seg_result = response['seg_image']
        region_results = response['region_result']

        for result in cls_result :
            clsResultModel = ClsResultModel.objects.create(image=image)

            final_label = ''
            label_list = []
            label_names = ['crack', 'lane', 'patch', 'normal']
            for label in result['label']:
                if label['description'] in label_names:
                    label_list.append(label)
            labels = sorted(label_list, key=lambda label_list: (label_list['score']), reverse=True)
            final_label = labels[0]['description']

            if labels[0]['description'] == 'crack':
                label_list = []
                detail_label_names = ['lc', 'tc', 'ac', 'detail_norm']
                for label in result['label']:
                    if label['description'] in detail_label_names:
                        label_list.append(label)
                labels = sorted(label_list, key=lambda label_list: (label_list['score']), reverse=True)
                if labels[0]['description'] == 'detail_norm':
                    final_label = 'normal'
                else:
                    final_label = labels[0]['description']

            clsResultModel.label = final_label
            clsResultModel.x = result['position']['x']
            clsResultModel.y = result['position']['y']
            clsResultModel.w = result['position']['w']
            clsResultModel.h = result['position']['h']
            clsResultModel.save()

        print(region_results)
        for region in region_results :
            region_area = region['region_area']
            regionResultModel = RegionResultModel.objects.create(image=image)
            regionResultModel.region_num = region['region']
            regionResultModel.region_type = region['region_type']

            # if region['distress_width'] == "null" :
            #     regionResultModel.distress_width = None
            # else :
            #     regionResultModel.distress_width = region['distress_width']
            #
            # if region['distress_height'] == "null":
            #     regionResultModel.distress_height = None
            # else :
            #     regionResultModel.distress_height = region['distress_height']
            #
            # if region['distress_area'] == "null":
            #     regionResultModel.distress_area = None
            # else :
            #     regionResultModel.distress_area = region['distress_area']
            # if region['distress_serverity'] == "null":
            #     regionResultModel.distress_serverity = None
            # else :
            #     regionResultModel.distress_serverity = region['distress_serverity']


            for patch in region_area :
                regionPositionModel = RegionPositionModel.objects.create(region_model=regionResultModel)


                regionPositionModel.x = patch['x']
                regionPositionModel.y = patch['y']
                regionPositionModel.w = patch['w']
                regionPositionModel.h = patch['h']
                regionPositionModel.save()
            regionResultModel.save()


        # Save segmentation result
        segResultModel = SegResultModel.objects.create(image=image)
        seg_img_path = os.path.join(str(image.image).split(".")[0] + "_seg" + ".png")
        segResultModel.seg_image = ContentFile(base64.b64decode(seg_result), name=seg_img_path)
        segResultModel.save()
        return HttpResponse(json.dumps({"state": True}), 'application/json')
    else:
        return HttpResponse(json.dumps({"state": False}), 'application/json')
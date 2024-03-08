# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageGTUploadForm, ImageUploadForm
from .models import *
from .utils.AnalysisRequest import AnalysisRequest

import json, os, base64
from CrackViewer.utils.segImagePostProcess import *


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
    if request.method == "POST":
        files = request.FILES.getlist('images')

        for file in files:
            instance = ImageModel(image=file)
            instance.save()

        return redirect('/imagelist/')
    else:
        return redirect('/imagelist/')


def image_list(request) :
    image_models = ImageModel.objects.all().order_by('-pk')
    seg_results = []
    for image_model in image_models:
        seg_result_models = SegResultModel.objects.filter(image=image_model.token)
        if len(seg_result_models) > 0:
            seg_result = seg_result_models[0]
        else:
            seg_result = None
        seg_results.append(seg_result)


    region_connectivity = []
    region_noise_filter = []
    severity_threshold = []

    for image_model in image_models :
        region_connectivity.append(image_model.region_connectivity)
        region_noise_filter.append(image_model.region_noise_filter)
        severity_threshold.append(image_model.severity_threshold)

    return render(request, 'imagelist.html', {
        'images' : image_models,
        'seg_results': seg_results,
        'region_connectivitys': region_connectivity,
        'region_noise_filters': region_noise_filter,
        'severity_thresholds': severity_threshold,
    })

def image_detail(request, image_pk) :
    image = ImageModel.objects.filter(pk=image_pk)
    seg_result = SegResultModel.objects.filter(image=image_pk)
    seg_gt = SegGTModel.objects.filter(image=image_pk)
    is_analyzed = False
    is_gt = False
    seg_image_url = ""
    seg_image_th_url = ""
    seg_image_hl_url = ""
    seg_image_hl_th_url = ""
    if len(seg_result) > 0 :
        is_analyzed = True
        seg_image_url = str(seg_result[0].seg_image)
        seg_image_th_url = str(seg_result[0].seg_image_th)
        seg_image_hl_url = str(seg_result[0].seg_image_hl)
        seg_image_hl_th_url = str(seg_result[0].seg_image_hl_th)
    if len(seg_gt) > 0 :
        is_gt = True

    return render(request, 'imagedetail.html', {
                    'image': image[0],
                    'image_pk': image_pk,
                    'seg_result': seg_image_url,
                    'seg_th_result': seg_image_th_url,
                    'seg_hl_result': seg_image_hl_url,
                    'seg_hl_th_result': seg_image_hl_th_url,
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
            dict_crack['severity'] = crack.severity
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
            dict_region['severity_results'] = region.severity_results
            dict_region['patching_results'] = region.patching_results
            dict_region['pothole_results'] = region.pothole_results
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
def get_seg_images(request) :
    seg_results = {}
    if request.method == "POST" :
        seg_result = SegResultModel.objects.filter(image__pk=request.POST['image_pk'])
        if len(seg_result) > 0:
            seg_results['seg_result'] = '/media/' + str(seg_result[0].seg_image)
            seg_results['seg_th_result'] = '/media/' + str(seg_result[0].seg_image_th)
            seg_results['seg_hl_result'] = '/media/' + str(seg_result[0].seg_image_hl),
            seg_results['seg_hl_th_result'] = '/media/' + str(seg_result[0].seg_image_hl_th)

    return HttpResponse(json.dumps(seg_results), 'application/json')

@csrf_exempt
def get_patching(request) :
    region_result = RegionResultModel.objects.filter(image__pk=request.POST['image_pk']).filter(region_type='patch')
    regions = []
    for region in region_result :
        dict_region = {}
        dict_region['region_num'] = region.region_num
        dict_region['patchs'] = []
        patching_results = {}
        patching_results['patching_bbox_maxx'] = region.patching_results['patching_bbox_maxx']
        patching_results['patching_bbox_maxy'] = region.patching_results['patching_bbox_maxy']
        patching_results['patching_bbox_minx'] = region.patching_results['patching_bbox_minx']
        patching_results['patching_bbox_miny'] = region.patching_results['patching_bbox_miny']
        patching_results['patching_region_maxx'] = region.patching_results['patching_region_maxx']
        patching_results['patching_region_maxy'] = region.patching_results['patching_region_maxy']
        patching_results['patching_region_minx'] = region.patching_results['patching_region_minx']
        patching_results['patching_region_miny'] = region.patching_results['patching_region_miny']
        dict_region['patching_results'] = patching_results
        regions.append(dict_region)
    return HttpResponse(json.dumps({"regions": regions}), 'application/json')

@csrf_exempt
def get_image_result(request) :
    image_result = {}
    if request.method == "POST" :
        image = ImageModel.objects.filter(token=request.POST.get('image_pk'))
        if len(image) > 0:
            image_result['result'] = image[0].result

    return HttpResponse(json.dumps(image_result), 'application/json')

@csrf_exempt
def analysis(request) :
    result = []
    if request.method == "POST" :
        image = ImageModel.objects.filter(token=request.POST.get('image_pk'))[0]
        prev_cls_results = ClsResultModel.objects.filter(image__pk=request.POST['image_pk'])
        prev_seg_results = SegResultModel.objects.filter(image__pk=request.POST['image_pk'])
        prev_region_results = RegionResultModel.objects.filter(image__pk=request.POST['image_pk'])
        prev_region_positions = RegionPositionModel.objects.filter(region_model=prev_region_results)
        url = AnalysisURL.objects.filter(server_name="crackviewer")

        for result in prev_cls_results :
            result.delete()

        for result in prev_seg_results :
            os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/', str(result.seg_image)))
            os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/', str(result.seg_image_th)))
            os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/', str(result.seg_image_hl)))
            result.delete()

        for result in prev_region_results :
            result.delete()

        for result in prev_region_positions :
            result.delete()

        print("==== Deleted previous results ====")

        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/', str(image.image))

        # Send analysis request to crack-bridge-site
        analysis_request = AnalysisRequest()
        b_image = analysis_request.load_binary_image(image_path)

        region_threshold = int(request.POST['region_threshold'])
        region_connectivity = int(request.POST['region_connectivity'])
        region_noise_filter = int(request.POST['region_noise_filter'])
        severity_threshold = int(request.POST['severity_threshold'])

        image.region_connectivity = region_connectivity
        image.region_noise_filter = region_noise_filter
        image.severity_threshold = severity_threshold
        analysis_request.set_request_attr(
            url=url[0].url,
            image=b_image,
            region_threshold=region_threshold,
            region_connectivity=region_connectivity,
            region_noise_filter=region_noise_filter,
            severity_threshold=severity_threshold,
        )
        response = json.loads((analysis_request.send_request_message().content).decode("utf-8"))
        patch_size =  response['patch_size']
        image_height =  int(response['image_height'])
        image_width =  int(response['image_width'])
        response = response['results'][0]


        # Get classification result and segmentation result from response of crack-bridge-site
        cls_result = response['cls_result']
        region_results = response['region_result']
        seg_result = response['seg_image']
        seg_th_result = response['seg_image_th']

        print("cls_results save start")
        count = 0
        for result in cls_result :
            clsResultModel = ClsResultModel.objects.create(image=image)

            label_list = []
            label_names = ['crack', 'line', 'patch', 'normal', 'pothole']
            for label in result['label']:
                if label['description'] in label_names:
                    label_list.append(label)
            labels = sorted(label_list, key=lambda label_list: (label_list['score']), reverse=True)
            final_label = labels[0]['description']

            if labels[0]['description'] == 'crack':
                count += 1
                label_list = []
                detail_label_names = ['lc', 'tc', 'ac']
                for label in result['label']:
                    if label['description'] in detail_label_names:
                        label_list.append(label)
                labels = sorted(label_list, key=lambda label_list: (label_list['score']), reverse=True)
                final_label = labels[0]['description']

            clsResultModel.label = final_label
            clsResultModel.x = result['position']['x']
            clsResultModel.y = result['position']['y']
            clsResultModel.w = result['position']['w']
            clsResultModel.h = result['position']['h']
            if final_label in ['lc', 'tc', 'ac'] :
                clsResultModel.severity = result['severity']
            clsResultModel.save()
        print("cls_results save end ", count)

        print("region_results save start", len(region_results))
        regions = []
        for region in region_results :
            dict_region = {}
            region_area = region['region_area']
            regionResultModel = RegionResultModel.objects.create(image=image)
            regionResultModel.region_num = region['region']
            dict_region['region_num'] = region['region']
            regionResultModel.region_type = region['region_type']
            dict_region['region_type'] = region['region_type']
            dict_region['patchs'] = []
            if region['region_type'] in ['lc', 'tc', 'ac'] :
                severity_results = {}
                severity_results['total_max_width'] = region['total_max_width']
                severity_results['total_average_width'] = region['total_average_width']
                severity_results['max_width_x'] = region['max_width_x']
                severity_results['max_width_y'] = region['max_width_y']
                severity_results['maxx'] = region['maxx']
                severity_results['maxy'] = region['maxy']
                severity_results['minx'] = region['minx']
                severity_results['miny'] = region['miny']
                severity_results['severity'] = region['severity']
                regionResultModel.severity_results = severity_results
                dict_region['severity_results'] = severity_results
            elif region['region_type'] == 'patch' :
                patching_results = {}
                patching_results['area'] = region['area']
                patching_results['patching_bbox_minx'] = region['patching_bbox_minx']
                patching_results['patching_bbox_miny'] = region['patching_bbox_miny']
                patching_results['patching_bbox_maxx'] = region['patching_bbox_maxx']
                patching_results['patching_bbox_maxy'] = region['patching_bbox_maxy']
                patching_results['patching_region_minx'] = region['patching_region_minx']
                patching_results['patching_region_miny'] = region['patching_region_miny']
                patching_results['patching_region_maxx'] = region['patching_region_maxx']
                patching_results['patching_region_maxy'] = region['patching_region_maxy']
                regionResultModel.patching_results = patching_results
                dict_region['patching_results'] = patching_results
            elif region['region_type'] == 'pothole' :
                pothole_results = {}
                pothole_results['area'] = region['area']
                pothole_results['pothole_bbox_minx'] = region['pothole_bbox_minx']
                pothole_results['pothole_bbox_miny'] = region['pothole_bbox_miny']
                pothole_results['pothole_bbox_maxx'] = region['pothole_bbox_maxx']
                pothole_results['pothole_bbox_maxy'] = region['pothole_bbox_maxy']
                pothole_results['pothole_region_minx'] = region['pothole_region_minx']
                pothole_results['pothole_region_miny'] = region['pothole_region_miny']
                pothole_results['pothole_region_maxx'] = region['pothole_region_maxx']
                pothole_results['pothole_region_maxy'] = region['pothole_region_maxy']
                regionResultModel.pothole_results = pothole_results
                dict_region['pothole_results'] = pothole_results
            else :
                print(region['region_type'])

            for patch in region_area :
                regionPositionModel = RegionPositionModel.objects.create(region_model=regionResultModel)
                regionPositionModel.x = patch['x']
                regionPositionModel.y = patch['y']
                regionPositionModel.w = patch['w']
                regionPositionModel.h = patch['h']
                regionPositionModel.save()
            regionResultModel.save()
            regions.append(dict_region)
        print("region_results save end")

        csv_contents = generate_csv_contents(regions)
        image.result = csv_contents
        image.save()

        # Save segmentation result
        segResultModel = SegResultModel.objects.create(image=image)
        seg_img_path = os.path.join(str(image.image).split(".")[0] + "_seg" + ".png")
        seg_img_th_path = os.path.join(str(image.image).split(".")[0] + "_seg_th" + ".png")
        seg_img_hl_path = os.path.join(str(image.image).split(".")[0] + "_seg_hl" + ".png")

        print("seg_image save start")

        segResultModel.seg_image = ContentFile(base64.b64decode(seg_result), name=seg_img_path)
        print("seg_image save")
        segResultModel.seg_image_th = ContentFile(base64.b64decode(seg_th_result), name=seg_img_th_path)
        print("seg_image_th save")
        segResultModel.seg_image_hl = ContentFile(base64.b64decode(seg_th_result), name=seg_img_hl_path)
        print("seg_image_hl save")
        segResultModel.save()

        seg_img_th_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/', seg_img_th_path)
        seg_img_hl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../media/', seg_img_hl_path)

        save_image_hightlight_region(seg_img_th_path, seg_img_hl_path, region_results, patch_size, image_height, image_width)

        return HttpResponse(json.dumps({"state": True}), 'application/json')
    else:
        return HttpResponse(json.dumps({"state": False}), 'application/json')


def generate_csv_contents(regions):
    results = "영역,균열종류,길이(m),면적(m²),최대 균열양(mm),심각도\n"
    for i, region in enumerate(regions):
        region_type = region['region_type']
        if region_type == "patch":
            text = "PAT"
        elif region_type == "ac":
            text = "AC"
        elif region_type == "lc":
            text = "LC"
        elif region_type == "tc":
            text = "TC"
        elif region_type == "pothole":
            text = "POT"

        if text == "PAT" or text == 'POT':
            area = region['patching_results']['area'] / 1000000 if text == "PAT" else region['pothole_results']['area'] / 1000000
            area_str = "{:.3f}".format(area)
            area_upper, floor = area_str.split('.')
            crack_area = "{}.{}".format(comma(int(area_upper)), floor)
            crack_width = "-"
            severity_area = "-"
            severity_severity = "-"
        elif text in ["LC", "TC"]:
            maxx = region['severity_results']['maxx']
            maxy = region['severity_results']['maxy']
            minx = region['severity_results']['minx']
            miny = region['severity_results']['miny']
            total_max_width = region['severity_results']['total_max_width']
            severity = capitalize_first_letter(str(region['severity_results']['severity']))

            width = maxx - minx
            height = maxy - miny

            length = height / 1000 if text == "LC" else width / 1000
            crack_width = "{:.3f}".format(length)
            crack_area = "-"
            severity_area = "{:.2f}".format(float(total_max_width))
            severity_severity = severity
        else:
            maxx = region['severity_results']['maxx']
            maxy = region['severity_results']['maxy']
            minx = region['severity_results']['minx']
            miny = region['severity_results']['miny']
            total_max_width = region['severity_results']['total_max_width']
            severity = capitalize_first_letter(str(region['severity_results']['severity']))
            width = maxx - minx

            area = ((maxx - minx) * (maxy - miny) / 1000000)
            area_str = "{:.3f}".format(area)
            area_upper, floor = area_str.split('.')
            crack_area = "{}.{}".format(comma(int(area_upper)), floor)
            crack_width = "-"
            severity_area = "{:.2f}".format(float(total_max_width))
            severity_severity = severity
        result =  "{},{},{},{},{},{}\n".format(i+1, text, crack_width, crack_area, severity_area, severity_severity)
        results += result
    return results


def capitalize_first_letter(s):
    return s.capitalize()

def comma(value):
    return "{:,}".format(value)
import requests
import json

class AnalysisRequest :
    def __init__(self):
        self.__url = None
        self.__json_data = None
        self.__json_file = None

    def set_request_attr(self, url, image, modules=None, region_threshold=0, region_connectivity=0, region_noise_filter=0, severity_threshold=200):
        self.__url = url
        self.__json_file = {'image': image}
        if modules is not None :
            self.__json_data = {
                'modules':modules,
                'region_threshold': region_threshold,
                'region_connectivity': region_connectivity,
                'region_noise_filter': region_noise_filter,
                'severity_threshold': severity_threshold
            }
        else :
            self.__json_data = {}

    def get_request_attr(self):
        return self.__url, self.__json_data, self.__json_file

    def send_request_message(self):
        try :
            response = requests.post(url=self.__url, data=self.__json_data, files=self.__json_file)
        except :
            response = {}

        return response

    def load_binary_image(self, image_path) :
        b_image = open(image_path, 'rb')
        return b_image
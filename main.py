import os
from PIL import Image, ExifTags

# img_contents = os.listdir()

img_folder = r"C:\Users\Jules\Documents\GeoSetter\img"
img_contents = os.listdir(img_folder)


class image_metadata:
    def __init__(self,path):
        self.path = path
        self.gps_info = ""
        self.DateTimeOriginal = ""
        self.date = ""
        self.time_of_day = ""

    def time_of_day_to_second(self,time):
        l_time = time.split(":")
        self.time_of_day = int(l_time[0])*60*60+int(l_time[1])*60+int(l_time[2])

    def DateTimeOriginal_formating(self):
        self.date = self.DateTimeOriginal.split(" ")[0]
        self.time_of_day_to_second(self.DateTimeOriginal.split(" ")[1])


def metadata_extraction(l_obj):
    for image in img_contents:
        full_path = os.path.join(img_folder, image)
        img = Image.open(full_path)
        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}

        l_obj.append(image_metadata(full_path))
        obj = l_obj[-1]
        obj.DateTimeOriginal = exif['DateTimeOriginal']
        obj.DateTimeOriginal_formating()
        try:
            obj.gps_info = exif['GPSInfo']
        except:
            obj.gps_info = []
            print("This image has no GPS info in it")
            print(full_path)


l_obj_image_metadata = []

metadata_extraction(l_obj_image_metadata)
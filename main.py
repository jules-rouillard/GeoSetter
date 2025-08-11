import os
from PIL import Image, ExifTags

# img_contents = os.listdir()

img_folder = rb"C:\Users\Jules\Documents\GeoSetter\img"
img_contents = os.listdir(img_folder)

class image_metadata:
    def __init__(self,name,path):
        self.name = name
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
        print(image)
        full_path = os.path.join(img_folder, image)
        l_obj.append(image_metadata(image,full_path))

        img = Image.open(full_path)
        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}

        obj = l_obj[-1]
        obj.DateTimeOriginal = exif['DateTimeOriginal']
        obj.DateTimeOriginal_formating()
        try:
            obj.gps_info = exif['GPSInfo']
        except:
            obj.gps_info = []
            print("This image has no GPS info in it")
            print(full_path)
        img.close()



def find_closer_time():


    return True

# def write_geo_metadata(obj,obj2):
#     img = Image.open(obj.path)
    
#     exif_data = img.getexif()
#     exif_data['GPSInfo'] = obj2.gps_info

#     img.save("modified_example.jpg", exif=exif_data)
#     img.close()
#     return True


l_obj_image_metadata = []

metadata_extraction(l_obj_image_metadata)

# write_geo_metadata(l_obj_image_metadata[0],l_obj_image_metadata[1])
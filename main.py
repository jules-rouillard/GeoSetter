import os
import sys
from PIL import Image, ExifTags
import piexif

class image_metadata:
    '''
    A class to store metadata of an image, including its name, path, GPS information, original date and time, and time of day in seconds.
    Attributes:
        
    '''
    def __init__(self,name,path):
        self.name = name
        self.path = path
        self.gps_info = ""

        self.GPSLatitudeRef =""
        self.GPSLatitude = ""
        self.GPSLongitudeRef = ""
        self.GPSLongitude = ""
        self.GPSAltitudeRef = ""
        self.GPSAltitude = ""
        self.gps_info = []

        self.DateTimeOriginal = ""
        self.date = ""
        self.time_of_day = ""

    def time_of_day_to_second(self,time):
        l_time = time.split(":")
        self.time_of_day = int(l_time[0])*60*60+int(l_time[1])*60+int(l_time[2])

    def DateTimeOriginal_formating(self):
        self.date = self.DateTimeOriginal.split(" ")[0]
        self.time_of_day_to_second(self.DateTimeOriginal.split(" ")[1])




def metadata_extraction(l_obj,img_folder,img_contents):
    '''
    Extract metadata from images in a folder and populate a list of image_metadata objects.
    1. Loop through each image in the specified folder. 
    2. For each image, create an image_metadata object and append it to the provided list.
    3. Open the image and extract its EXIF data, specifically the DateTimeOriginal and GPSInfo.
    4. Update the corresponding image_metadata object with the extracted data.
    Args:
        l_obj (list): A list to store image_metadata objects.
        img_folder (str): The path to the folder containing images.
        img_contents (list): A list of image filenames in the folder.
    Returns:
        None
    '''
    for image in img_contents:
        full_path = os.path.join(img_folder, image)
        l_obj.append(image_metadata(image,full_path))

        obj = l_obj[-1]
        print(obj.path)
        # See _exif.py for ifd and tag
    
        # GPSLatitudeRef = 1
        # GPSLatitude = 2
        # GPSLongitudeRef = 3
        # GPSLongitude = 4
        # GPSAltitudeRef = 5
        # GPSAltitude = 6

        # DateTime = 306

        img = Image.open(full_path)

        # Load existing EXIF data
        exif_dict = piexif.load(img.info["exif"])


        obj.DateTimeOriginal = exif_dict["0th"][306].decode('UTF-8')
        obj.DateTimeOriginal_formating()

        try:
            for i in range(1,7):
                obj.gps_info.append(exif_dict["GPS"][i])
                # print(piexif.TAGS["GPS"][i]["name"], exif_dict["GPS"][i])
        except:
            print("This image has no GPS info in it")

        print(obj.gps_info)
        # print(obj.DateTimeOriginal)
        print(obj.date)
        print(obj.time_of_day)
        print("---------------------------")
        img.close()



def find_closer_time():
    
    return True

def write_geo_metadata(obj_gps,obj2_no_gps):
    # Write 

    img = Image.open(obj2_no_gps.path)

    # Load existing EXIF data
    exif_dict = piexif.load(img.info["exif"])

    # Modify metadata
    for i in range(1,7):
        # piexif.GPSIFD.GPSLatitudeRef = 1
        exif_dict["GPS"][i] = obj_gps.gps_info[i-1]
    

    # Convert back to bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save image with new metadata
    img.save("output.jpg", exif=exif_bytes)

    img.close()

    return True



img_folder = rb"C:\Users\Jules\Documents\GeoSetter\img2"
img_contents = os.listdir(img_folder)
l_obj_image_metadata = []


metadata_extraction(l_obj_image_metadata,img_folder,img_contents)


write_geo_metadata(l_obj_image_metadata[0],l_obj_image_metadata[1])
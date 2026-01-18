import os
import sys
from PIL import Image, ExifTags
import piexif
import customtkinter

class image_metadata:
    '''
    A class to store metadata of an image, including its name, path, GPS information, original date and time, and time of day in seconds.
    Attributes:
        
    '''
    def __init__(self,name,path):
        self.name = name
        self.path = path

        self.gps_info = []
        # self.

        self.DateTimeOriginal = ""
        self.date = ""
        self.time_of_day_second = ""

    def time_of_day_to_second(self,time):
        l_time = time.split(":")
        self.time_of_day_second = int(l_time[0])*60*60+int(l_time[1])*60+int(l_time[2])

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

        img = Image.open(full_path)

        # Load existing EXIF data
        exif_dict = piexif.load(img.info["exif"])

        # See _exif.py for ifd and tag
        # DateTime = 306
        obj.DateTimeOriginal = exif_dict["0th"][306].decode('UTF-8')
        obj.DateTimeOriginal_formating()

        try:
            # GPSLatitudeRef = 1
            # GPSLatitude = 2
            # GPSLongitudeRef = 3
            # GPSLongitude = 4
            # GPSAltitudeRef = 5
            # GPSAltitude = 6
            for i in range(1,7):
                obj.gps_info.append(exif_dict["GPS"][i])
                # print(piexif.TAGS["GPS"][i]["name"], exif_dict["GPS"][i])
        except:
            print("This image has no GPS info in it")

        print(obj.gps_info)
        print(obj.date)
        print(obj.time_of_day_second)
        print("---------------------------")
        img.close()

def split_obj_on_gps_info(l_obj):
    l_obj_w_gps = []
    l_obj_no_gps = []
    for obj in l_obj:
        if obj.gps_info == []:
            l_obj_no_gps.append(obj)
        else:
            l_obj_w_gps.append(obj)
    # print(l_obj_w_gps)
    # print(l_obj_no_gps)
    return l_obj_w_gps,l_obj_no_gps

def find_closer_time(l_obj_w_gps,l_obj_no_gps,threshold=1*60*60):

    for obj_no_gps in l_obj_no_gps:
        temp_gps_info = []
        delta_time = threshold+1000
        for obj_w_gps in l_obj_w_gps:
            
            if obj_no_gps.date == obj_w_gps.date:

                delta_time_temp = abs(obj_no_gps.time_of_day_second - obj_w_gps.time_of_day_second)

                if delta_time_temp <= threshold and delta_time_temp < delta_time:
                    delta_time = delta_time_temp
                    temp_gps_info = obj_w_gps.gps_info

        obj_no_gps.gps_info = temp_gps_info
        print(obj_no_gps.name)
        print(obj_no_gps.gps_info)

    return True

def write_geo_metadata(obj):
    # Write 
    # Open image to edit
    img = Image.open(obj.path)
    # Load existing EXIF data
    exif_dict = piexif.load(img.info["exif"])
    # Modify metadata
    for i in range(1,7):
        # piexif.GPSIFD.GPSLatitudeRef = 1
        exif_dict["GPS"][i] = obj.gps_info[i-1]

    # Convert back to bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save image with new metadata
    img.save(obj.name.decode('UTF-8')+".jpg", exif=exif_bytes)
    img.close()

    return True


# Testing tool
img_folder = rb"C:\Users\Jules\Documents\GeoSetter\img"
output_folder = rb"C:\Users\Jules\Documents\GeoSetter\img2"
img_contents = os.listdir(img_folder)
l_obj_image_metadata = []

print("Metadata extraction")
metadata_extraction(l_obj_image_metadata,img_folder,img_contents)

print("Split list in two")
l_obj_w_gps,l_obj_no_gps = split_obj_on_gps_info(l_obj_image_metadata)

print("Finding close picture and taking gps data")
find_closer_time(l_obj_w_gps,l_obj_no_gps)

for obj in l_obj_no_gps:
    if obj.gps_info != []:
        write_geo_metadata(obj)



customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("400x240")
app.title("GeoSetter beta")

# t1_File_1_text = app.Label(text="File 1 (.lckt/.cap)").grid(row=0, column=0)


app.mainloop()
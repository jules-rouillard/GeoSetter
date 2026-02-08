import os
import sys
from PIL import Image, ExifTags
import piexif
# For GUI
import customtkinter as tk
from customtkinter import filedialog as fd

# Using some global variable at the end with the GUI; Could be better

class image_metadata:
    '''
    A class to store metadata of an image, including its name, path, GPS information, original date and time, and time of day in seconds.
    Attributes:
        
    '''
    def __init__(self,name,path):
        self.name = name
        self.path = path

        self.gps_info = []
        self.has_match = False
        self.matched_obj = None
        self.cktimage = None
        
        self.DateTimeOriginal = ""
        self.date = ""
        self.time_of_day_second = ""

    def time_of_day_to_second(self,time):
        l_time = time.split(":")
        self.time_of_day_second = int(l_time[0])*60*60+int(l_time[1])*60+int(l_time[2])

    def DateTimeOriginal_formating(self):
        self.date = self.DateTimeOriginal.split(" ")[0]
        self.time_of_day_to_second(self.DateTimeOriginal.split(" ")[1])



def metadata_extraction(l_obj,img_folder):
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
    img_contents = os.listdir(img_folder)
    for image in img_contents:
        full_path = os.path.join(img_folder, image)
        # Issue due to .mp4 files in the directory need to expand compatibility to other image format for now only .jpg

        if (full_path[-4:-1]+full_path[-1]).lower() == ".jpg":
            l_obj.append(image_metadata(image,full_path))
            obj = l_obj[-1]
            print(obj.path)
        
            img = Image.open(full_path)

            # obj.cktimage  = tk.CTkImage(light_image=img,dark_image=img,size=(523,402))
            obj.cktimage  = tk.CTkImage(light_image=Image.open(full_path),
                                        dark_image=Image.open(full_path),
                                        size=(450,375))

            # Verify if exif data exist as it will crash when trying to load none existing data
            exif_dict = img.info.get("exif") 

            if exif_dict:
                # Load existing EXIF data
                exif_dict = piexif.load(img.info["exif"])

                # See _exif.py for ifd and tag
                # DateTime = 306
                try:
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
                except:
                    # Some if not time for match removed from list
                    l_obj.remove(obj)
                    print("NO EXIF DATA FOR MATCH")
                    print("---------------------------")


            else :
                # Data does not exist we ignore picture (No data => no time stamp nothing to match)
                l_obj.remove(obj)
                print("NO EXIF DATA")
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
                    obj_no_gps.gps_info = obj_w_gps.gps_info
                    obj_no_gps.has_match = True
                    obj_no_gps.matched_obj = obj_w_gps


        print(obj_no_gps.name)
        print(obj_no_gps.gps_info)

    return True

def write_geo_metadata(obj,safe_mode):
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
    if safe_mode:
        img.save("gps_"+obj.name, exif=exif_bytes)
    else:
        img.save(obj.name, exif=exif_bytes)
    img.close()

    return True

def save_results(vars):
    # Saving the image with metadata added

    cwd = os.getcwd()
    os.chdir(vars.output_folder)
    for obj in vars.l_obj_no_gps:
        if obj.gps_info != []:
            write_geo_metadata(obj,vars.safe_mode)
    os.chdir(cwd)

#################################### GUI ####################################

#### UI FUNCTION ###

# Selection of directory
def select_dir(text_entry):
    fname = fd.askdirectory(initialdir=os.path.dirname(os.path.abspath(__file__)))
    text_entry.set(fname)

# Automatic unticking of options
def tick_checkbtn(btn):
    for i in range(len(l2)):
        if l2[i] != btn:
            if l2[i].get():
                l2[i].deselect()

class variable_for_ui:
    # Use to keep some of the variable together, reducing the use of global one.
    # For now I will not add the tinker variable to this class, too many of them
    def __init__(self):
        self.l_obj_image_metadata = []
        self.l_obj_w_gps = []
        self.l_obj_no_gps = []

        self.input_folder = None
        self.output_folder = None

        self.idx_img_display = 0
        self.run_info = ""
        self.nb_match_found = 0
        self.safe_mode = False

    def find_number_image_w_match_found(self):
        self.nb_match_found = 0
        for i in range(len(self.l_obj_no_gps)):
            if (self.l_obj_no_gps[i].has_match):
                self.nb_match_found += 1

    def get_run_info(self):
        self.find_number_image_w_match_found()
        self.run_info = ("Nb Images="+str(len(self.l_obj_image_metadata))+
                "; GPS="+str(len(self.l_obj_w_gps))+
                "; No GPS="+str(len(self.l_obj_no_gps))+
                "; Match Found=" +str(self.nb_match_found))


run_var = variable_for_ui()

def main_run(run_vars,type):
    str_stat.set("Processing")
    run_vars.input_folder = str_input_dir.get()
    run_vars.output_folder = str_output_dir.get()

    run_var.safe_mode = btn_safe_mode.get()

    if run_vars.input_folder == "":
        return False

    if run_vars.output_folder == "":
        run_vars.output_folder = os.getcwd()


    run_vars.l_obj_image_metadata = []
    print("Metadata extraction")
    metadata_extraction(run_vars.l_obj_image_metadata,run_vars.input_folder)

    print("Split list in two")
    run_vars.l_obj_w_gps,run_vars.l_obj_no_gps = split_obj_on_gps_info(run_vars.l_obj_image_metadata)

    print("Finding close picture and taking gps data")
    find_closer_time(run_vars.l_obj_w_gps,run_vars.l_obj_no_gps,60*60)
    
    run_vars.get_run_info()
    str_run_info.set(run_vars.run_info)

    if type == "run":
        save_results(run_vars)
        str_stat.set("Run Done")

    else:
        str_stat.set("Scan Done")


def img_display_change(run_vars,control):
    size_list = len(run_var.l_obj_no_gps)

    if size_list > 0:
        run_vars.idx_img_display = (run_vars.idx_img_display + control)%size_list
        
        if run_vars.l_obj_no_gps[run_vars.idx_img_display].has_match :
            str_image_status.set("MATCHED")
            obj_no_gps = run_vars.l_obj_no_gps[run_vars.idx_img_display]
            obj_matched = obj_no_gps.matched_obj

            image_no_gps.configure(image=obj_no_gps.cktimage)
            image_matched_to.configure(image=obj_matched.cktimage)
        else:
            str_image_status.set("NOT MATCHED")
            image_no_gps.configure(image=run_vars.l_obj_no_gps[run_vars.idx_img_display].cktimage)
            image_matched_to.configure(image=run_vars.l_obj_no_gps[run_vars.idx_img_display].cktimage)


### UI Instance ###

tk.set_appearance_mode("System")  # Modes: system (default), light, dark
tk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = tk.CTk()  # create CTk window like you do with the Tk window
app.geometry("470x1100")
app.title("GeoSetter")

str_input_dir = tk.StringVar()
textbox_input_dir = tk.CTkEntry(app, textvariable=str_input_dir).place(x = 10, y = 50)
button = tk.CTkButton(app, text="Input directory", command=lambda: select_dir(str_input_dir))
button.place(x = 160, y = 50)

str_output_dir = tk.StringVar()
textbox_output_dir = tk.CTkEntry(app, textvariable=str_output_dir).place(x = 10, y = 100)
button2 = tk.CTkButton(app, text="Output directory", command=lambda: select_dir(str_output_dir))
button2.place(x = 160, y = 100)

# space with gap 150

# RUN OPTIONS

# Safe mode ie no overwriting original pictures
btn_safe_mode = tk.CTkCheckBox(app, text="Safe mode")
btn_safe_mode.place(x = 310, y = 50)
btn_safe_mode.select()
run_var.safe_mode = btn_safe_mode.get()

# Button to select search range
btn_1h = tk.CTkCheckBox(app, text="1H", command=lambda: tick_checkbtn(btn_1h))
btn_1h.place(x = 310, y = 75)

btn_2h = tk.CTkCheckBox(app, text="2H", command=lambda: tick_checkbtn(btn_2h))
btn_2h.place(x = 310, y = 100)

btn_3h = tk.CTkCheckBox(app, text="3H", command=lambda: tick_checkbtn(btn_3h))
btn_3h.place(x = 310, y = 125)

btn_scan = tk.CTkButton(app, text="SCAN", command=lambda: main_run(run_var,"scan"))
btn_scan.place(x = 10, y = 150)

btn_run = tk.CTkButton(app, text="RUN", command=lambda: main_run(run_var,"run"))
btn_run.place(x = 160, y = 150)

l2 = [btn_1h,btn_2h,btn_3h]


# RUN INFO
str_stat = tk.StringVar()
str_stat.set("")
t_status = tk.CTkLabel(app, textvariable=str_stat)
t_status.place(x = 25, y = 200)

str_run_info = tk.StringVar()
t_run_info = tk.CTkLabel(app, textvariable=str_run_info)
t_run_info.place(x = 100, y = 200)

# size=(525,400)

image_no_gps = tk.CTkLabel(app, text="", text_color="white")  # display image with a CTkLabel
image_no_gps.place(x = 10, y = 275)

image_matched_to = tk.CTkLabel(app, text="", text_color="white")  # display image with a CTkLabel
image_matched_to.place(x = 10, y = 700)

btn_img_prev = tk.CTkButton(app, text="<", command=lambda: img_display_change(run_var,-1))
btn_img_prev.place(x = 10, y = 225)

btn_img_next = tk.CTkButton(app, text=">", command=lambda: img_display_change(run_var,1))
btn_img_next.place(x = 160, y = 225)

str_image_status = tk.StringVar()
t_image_status = tk.CTkLabel(app, textvariable=str_image_status)
t_image_status.place(x = 235, y = 650)


app.mainloop()


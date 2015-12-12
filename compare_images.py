from Tkinter import*
import os.path
import tkMessageBox
from osgeo import gdal
import glob
gdal.UseExceptions()
from tkFileDialog import askopenfilename,askdirectory
import time
import math

import numpy as np

from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

class Rectangle:
    def __init__(self,x_val,y_val,w,h):
        self.x = x_val
        self.y = y_val
        self.width = w
        self.height = h
    def __str__(self):
        return "({0},{1},{2},{3}".format(self.x,self.y,self.width,self.height)



class Main:
    def __init__(self,master):
        #Method for getting the input directory for folder1 images
        def open_folder1():
            foldername = askdirectory()
            foldername = foldername.replace("/","\\")
            self.folder1_entry.delete(0,END)
            self.folder1_entry.insert(0,foldername)

        #Method for getting the input directory for folder2 images
        def open_folder2():
            foldername = askdirectory()
            foldername = foldername.replace("/","\\")
            self.folder2_entry.delete(0,END)
            self.folder2_entry.insert(0,foldername)


        #Method for comparing two images of same width and height
        def comapare_images(input1,input2,f,filename,window):
            start = time.time()
            #parse the filename to get only the title
            filename1=input1.split("\\")
            filename1 = filename1[len(filename1)-1]

            filename2=input2.split("\\")
            filename2 = filename2[len(filename2)-1]

            ###Import the file data 1
            data1 = gdal.Open(input1)
            ###Read the data into a 2D array
            r1_layer = data1.GetRasterBand(1)
            g1_layer = data1.GetRasterBand(2)
            b1_layer = data1.GetRasterBand(3)

            r1_data = r1_layer.ReadAsArray()
            g1_data = g1_layer.ReadAsArray()
            b1_data = b1_layer.ReadAsArray()


            ###Import data from file 2
            data2 = gdal.Open(input2)
            r2_layer = data2.GetRasterBand(1)
            g2_layer = data2.GetRasterBand(2)
            b2_layer = data2.GetRasterBand(3)

            r2_data = r2_layer.ReadAsArray()
            g2_data = g2_layer.ReadAsArray()
            b2_data = b2_layer.ReadAsArray()


            print "Comparing " + str(filename1) + " & " + str(filename2)
            # Create a report.csv file and add headers

            max_height = 1229
            max_width = 1843

            for x in range (window.x, max_width,window.width):
                window.y = 0
                for y in range(window.y, max_height,window.height):
                    r1_data_sliced = r1_data[window.x:window.x+window.width,window.y:window.y+window.height]
                    g1_data_sliced = g1_data[window.x:window.x+window.width,window.y:window.y+window.height]
                    b1_data_sliced = b1_data[window.x:window.x+window.width,window.y:window.y+window.height]

                    r2_data_sliced = r2_data[window.x:window.x+window.width,window.y:window.y+window.height]
                    g2_data_sliced = g2_data[window.x:window.x+window.width,window.y:window.y+window.height]
                    b2_data_sliced = b2_data[window.x:window.x+window.width,window.y:window.y+window.height]

                    r1_data_sliced_avg = np.mean(r1_data_sliced)
                    r2_data_sliced_avg = np.mean(r2_data_sliced)
                    g1_data_sliced_avg = np.mean(g1_data_sliced)
                    g2_data_sliced_avg = np.mean(g2_data_sliced)
                    b1_data_sliced_avg = np.mean(b1_data_sliced)
                    b2_data_sliced_avg = np.mean(b2_data_sliced)

                    rgb1 = sRGBColor(r1_data_sliced_avg, g1_data_sliced_avg, b1_data_sliced_avg, is_upscaled=True)
                    rgb2 = sRGBColor(r2_data_sliced_avg, g2_data_sliced_avg, b2_data_sliced_avg, is_upscaled=True)
                    lab1 = convert_color(rgb1, LabColor)
                    lab2 = convert_color(rgb2, LabColor)
                    delta_e = delta_e_cie2000(lab1, lab2)

                    if(delta_e >= 1):
                        f=open(filename + "_report.csv",'a')
                        f.write(filename1+","+filename2+","+str(x)+","+str(window.y)+","+str(r1_data_sliced_avg)+","+str(r2_data_sliced_avg)+","+str(g1_data_sliced_avg)+","+str(r2_data_sliced_avg)+","+str(b1_data_sliced_avg)+","+str(b2_data_sliced_avg)+","+str(delta_e)+"\n")
                        f.close()

                    window.y = window.y + 20
                    if(window.y > max_height):
                        window.width = 20 - (window.y - max_height)
                        window.y = max_height


        def run():
            folder1 = self.folder1_entry.get()
            folder1.replace("\\","\\\\")
            folder1_files = glob.glob(folder1+"\\*.*")
            folder2 = self.folder2_entry.get()
            folder2.replace("\\","\\\\")
            folder2_files = glob.glob(folder2+"\\*.*")

            for x in range(0,len(folder1_files)):
                filename=folder2_files[x].split("\\")
                filename = filename[len(filename)-1].split(".")[0]+"_"+filename[len(filename)-1].split(".")[1]+"."+filename[len(filename)-1].split(".")[2]
                f=open(filename + "_report.csv",'a')
                f.write("Filename1,Filename2,Pixel_X,Pixel_Y,R1_value,R2_value,G1_value,G2_value,B1_value,B2_Value,Delta_E\n")
                f.close()
                window = Rectangle(0,0,20,20)
                comapare_images(folder1_files[x],folder2_files[x],f,filename,window)

#############################################################################################################

        #Code for creating GUI
        #Create a frame for GUI
        self.master = master
        self.frame = Frame(self.master)
        self.title = Label(self.frame, text="Merge Rasters").grid(row=0,column=1,pady=5,columnspan=2)

        #Create label and input folder1 location
        self.folder1_dir = Label(self.frame, text="Original Files Location: ").grid(row=1)
        self.folder1_entry = Entry(self.frame,width=80)
        self.folder1_entry.grid(row=1,column=1,sticky=W,columnspan=2)
        self.button_sat = Button(self.frame,text="Browse",command=open_folder1,width=9)
        self.button_sat.grid(row=1,column=3,padx=10,sticky=W)

        #Create label and input folder2 location
        self.folder2_dir = Label(self.frame, text="Converted Files Location: ").grid(row=2)
        self.folder2_entry = Entry(self.frame,width=80)
        self.folder2_entry.grid(row=2,column=1,sticky=W,columnspan=2)
        self.button_dem = Button(self.frame,text="Browse",command=open_folder2,width=9)
        self.button_dem.grid(row=2,column=3,padx=10,sticky=W,pady=5)

        #Create process button
        self.B = Button(self.frame, text ="Comapare Images", command=run)
        self.B.grid(row=3,column=1,pady=5,columnspan=2)

        self.frame.pack()

#Main funtion to loop GUI
def main():
    root = Tk()
    root.resizable(0,0)
    root.wm_title("Comapare Images")

    app = Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()
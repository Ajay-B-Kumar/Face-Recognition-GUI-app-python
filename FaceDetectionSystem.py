from tkinter import *
import cv2
import facetrk as ftk
from PIL import Image, ImageTk
import time
import customtkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfile
import keyboard
import threading
import os
import shutil
import gc

faceDtk = ftk.facedetector()
faceMesh = ftk.FaceMeshDetector()
faceRec = ftk.FaceRecognizer()

# video capture
class VideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open the camera", video_source)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    def getFrame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
    
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            
def choose():
    f_types = [('Jpg Files', '*.jpg')]
    global filename
    filename = filedialog.askopenfilename(filetypes=f_types)
    if filename != "":
        global selected_img
        selected_img = Image.open(filename)
        width, height = selected_img.size
        img_resized=selected_img.resize((int(width/3),int(height/3)))
        img_pi = ImageTk.PhotoImage(img_resized)
        global pre
        pre = customtkinter.CTkButton(uploadImage,text="", image=img_pi, fg_color="transparent")
        pre.place(relx=0.5, rely=0.5, anchor=CENTER)
        global entry
        entry = customtkinter.CTkEntry(uploadImage, placeholder_text="Name")
        entry.place(relx=0.5, rely=0.80, anchor=CENTER)
        uploadButton.place(relx=0.5, rely=0.90, anchor=CENTER)
    else:
        # no file chosen
        
        nfc.place(relx=0.5, rely=0.5, anchor=CENTER)

    return

def uploadImg():
    frame.grid_forget()
    tutorialFrame.grid_forget()
    uploadImage.grid(row=0, column=1, padx=(5,20), pady=20, sticky="nsew", rowspan=1000)
    global progressLabel
    progressLabel.place_forget()
    if webcamOn :
        global vid
        vid.__del__()
    fdbutton.configure(state="normal")
    frbutton.configure(state="normal")
    choose()

def upload(selected_img,filename):
    # if  loading_label
    #     loading_label.destroy()
    global pre
    pre.place_forget()
    global entry
    filename=entry.get()+".jpg"
    entry.place_forget()
    uploadButton.place_forget()
    nfc.place_forget()
    global progressLabel
    progressLabel.configure(text="Training...", font=("Helvetica",20))
    progressLabel.place(relx=0.5, rely=0.4, anchor=CENTER)
    progressbar2.place(relx=0.5, rely=0.50, anchor=CENTER)
    progressbar2.configure(mode="indeterminate")
    progressbar2.start()

    def save_image():
        selected_img.save(os.path.join(path, os.path.basename(filename)))
        imglist.append(os.path.basename(filename))
        Train(faceRec, images, imglist, path, names)
        progressLabel.configure(text="Model Trained!", font=("Helvetica",25))
        progressLabel.place(relx=0.5, rely=0.5, anchor=CENTER)
        progressbar2.stop()
        progressbar2.place_forget()
        # progressbar2.destroy()

    thread = threading.Thread(target=save_image)
    thread.start()


def Train(faceRec,images,imglist,path,names):
    names.clear()
    images.clear()
    for label in imglist:
        currentimg = cv2.imread(f'{path}/{label}')
        images.append(currentimg)
        names.append(os.path.splitext(label)[0])
    print(names)
    global trainImgList
    trainImgList = faceRec.trainImgs(images)
    return trainImgList


def detectFace(start_webcam, loading_label, detection, names, trainImgList):
    if not start_webcam:
        return
    loading_label.configure(text="Starting webcam...", font=("Helvetica",20))
    loading_label.place(relx=0.5, rely=0.4, anchor=CENTER)
    global vid
    global webcamOn
    if not webcamOn:
        vid = VideoCapture(0)
    else:
        vid.__del__()
        vid = VideoCapture(0)
    webcamOn = True
    loading_label.configure(text="Press 'esc' key to stop")
    loading_label.place(relx=0.5, rely=0.95, anchor=CENTER)
    canvas.configure(width=vid.width,height=vid.height)
    canvas.place(relx=0.5, rely=0.55, anchor=CENTER)
    global name, faceDistance, img
    while True:
        if webcamOn:
            _, img = vid.getFrame()
            if _:
                progressbar.stop()
                progressbar.place_forget()
                
                if detection:
                    img, bbox = faceDtk.find_faces(img)
                else:
                    img, name, faceDistance = faceRec.recognize(img, trainImgList, names, name, faceDistance)
                    print(name, faceDistance)

                image_new = Image.fromarray(img)
                photo = ImageTk.PhotoImage(image=image_new)
                canvas.create_image(0, 0, image=photo, anchor=NW)
                canvas.photo = photo
            img = None
        if keyboard.is_pressed('esc'):
            break

    loading_label.place_forget()
    vid.__del__()
    canvas.place_forget()
    bg.place(relx=0.5, rely=0.55, anchor=CENTER)
    fdbutton.configure(state="normal")
    frbutton.configure(state="normal")
    webcamOn = False

def start_webcam(detection):
    uploadImage.grid_forget()
    tutorialFrame.grid_forget()
    frame.grid(row=0, column=1, padx=(5,20), pady=20, sticky="nsew", rowspan=1000)
    bg.place_forget()
    global webcamOn
    if webcamOn:
        vid.__del__()
    canvas.place_forget()

    print(detection)
    fdbutton.configure(state="disabled")
    frbutton.configure(state="disabled")
    loading_label.place(relx=0.5, rely=0.4, anchor=CENTER)
    global progresLabel
    progressbar.place(relx=0.5, rely=0.5, anchor=CENTER)
    progressbar.configure(mode="indeterminate")
    progressbar.start()
    threading.Thread(target=detectFace, args=(True, loading_label, detection, names, trainImgList)).start()

def tutorialpage():
    uploadImage.grid_forget()
    frame.grid_forget()
    if webcamOn :
        global vid
        vid.__del__()
    canvas2.place_forget()
    fdbutton.configure(state="normal")
    frbutton.configure(state="normal")
    tutorialFrame.grid(row=0,column=1, padx=(5,20), pady=20,sticky="nsew", rowspan=1000)
    # t_label.configure(text="Starting webcam...")
    # t_label.place(relx=0.5,rely=0.45,anchor=CENTER)

    threading.Thread(target=Mesh, args=(names,)).start()

def Mesh(names):
    if not start_webcam:
        return
    t_label.configure(text="Starting webcam...", font=("Helvetica",20))
    t_label.place(relx=0.5, rely=0.4, anchor=CENTER)
    t_progressBar.configure(mode="indeterminate")
    t_progressBar.place(relx=0.5,rely=0.5,anchor=CENTER)
    t_progressBar.start()
    global vid
    global webcamOn
    if not webcamOn:
        vid = VideoCapture(0)
    else:
        vid.__del__()
        vid = VideoCapture(0)
    webcamOn = True
    t_label.configure(text="Press 'esc' key to stop")
    t_label.place(relx=0.5, rely=0.95, anchor=CENTER)
    t_progressBar.stop()
    t_progressBar.place_forget()
    global img
    canvas2.configure(width=vid.width,height=vid.height)
    canvas2.place(relx=0.5, rely=0.55, anchor=CENTER)
    current_mode = 1
    start_time = time.time()
    while True:
        if webcamOn:
            _, img = vid.getFrame()
            if _:
                current_time = time.time()
                if current_time - start_time >= 5:
                    current_mode = (current_mode % 3) + 1
                    start_time = current_time

                if  current_mode == 2:
                    img, facelms = faceMesh.mesh(img)
                    cv2.rectangle(img, (0,0), (400,40), (0,200,0),cv2.FILLED)
                    cv2.putText(img, "2. Feature Extraction", (10,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255),2)
                elif current_mode == 3:
                    img = faceMesh.bmesh(img, names, faceDistance, name)
                    cv2.rectangle(img, (0,0), (369,40), (0,0,200),cv2.FILLED)
                    cv2.putText(img, "3. Face recognition", (10,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255),2)
                else:
                    img, bbox = faceDtk.find_faces(img)
                    cv2.rectangle(img, (0,0), (225,40), (200,0,0),cv2.FILLED)
                    cv2.putText(img, "1. Detection", (10,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255),2)
                image_new = Image.fromarray(img)
                photo = ImageTk.PhotoImage(image=image_new)
                canvas2.create_image(0, 0, image=photo, anchor=NW)
                canvas2.photo = photo
            img = None
        if keyboard.is_pressed('esc'):
            break

    loading_label.destroy()
    vid.__del__()
    canvas2.destroy()
    bg.place(relx=0.5, rely=0.55, anchor=CENTER)
    fdbutton.configure(state="normal")
    frbutton.configure(state="normal")
    webcamOn = False

def change_appearance_mode_event(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)

path = "Images"
images = []
names = []
imglist = os.listdir(path)
selected_img = None 
names.clear()
images.clear()
filename=""
trainImgList = []
trainImgList = Train(faceRec, images, imglist, path, names)
faceDistance = []
name = "Unknown"
webcamOn = False
img = None
vid = None
root = customtkinter.CTk()
customtkinter.set_appearance_mode('light')
root.geometry("720x480")
root.title("Facial Recognition System")

navigationFrame = customtkinter.CTkFrame(master=root, corner_radius=4)
navigationFrame.grid(row=0, column=0, padx=(20,5), pady=20, sticky="nsew", rowspan=50)

frame = customtkinter.CTkFrame(master=root, corner_radius=4)
frame.grid(row=0, column=1, padx=(5,20), pady=20, sticky="nsew", rowspan=1000)
canvas = Canvas(master=frame)

tutorialFrame = customtkinter.CTkFrame(master=root, corner_radius=4)
tutorialLabel = customtkinter.CTkLabel(master=tutorialFrame, text="Steps to Recognize Faces" ,font=customtkinter.CTkFont("Poor Richard",25, weight="bold"), fg_color=("white","gray30"),text_color=("skyblue","white"), corner_radius=5)
tutorialLabel.place(relx=0.5, rely=0.1, anchor=CENTER)
canvas2 = Canvas(master=tutorialFrame)
t_label = customtkinter.CTkLabel(master=tutorialFrame, text="")
t_progressBar = customtkinter.CTkProgressBar(master=tutorialFrame, orientation="horizontal")

logo = customtkinter.CTkLabel(frame,text="FACE DETECTION SYSTEM", font=customtkinter.CTkFont("Poor Richard",30, weight="bold"), fg_color=("white","gray30"),text_color=("skyblue","white"), corner_radius=5)
logo.place(relx=0.5, rely=0.1, anchor=CENTER)

bgimage = Image.open("bg.png")
bgimage = bgimage.resize((640,480),Image.ANTIALIAS)
bg_image = ImageTk.PhotoImage(bgimage)
bg = customtkinter.CTkLabel(frame, text="", image=bg_image, corner_radius=10)
bg.place(relx=0.5, rely=0.55, anchor=CENTER)

global loading_label
loading_label = customtkinter.CTkLabel(master=frame, text="")

root.grid_columnconfigure(1, weight=1)  # Make column 1 resizable
root.grid_rowconfigure(0, weight=1)    # Make row 0 resizable

progressbar = customtkinter.CTkProgressBar(master=frame, orientation="horizontal")

uploadImage = customtkinter.CTkFrame(master = root, corner_radius=4)
progressbar2 = customtkinter.CTkProgressBar(master=uploadImage, orientation="horizontal")
uploadButton = customtkinter.CTkButton(master=uploadImage, text="Upload", command= lambda :  upload(selected_img,filename))
addImage = customtkinter.CTkLabel(uploadImage,text="ADD NEW IMAGE", font=customtkinter.CTkFont("Poor Richard",30, weight="bold"), fg_color=("white","gray30"),text_color=("skyblue","white"), corner_radius=10)
addImage.place(relx=0.5, rely=0.1, anchor=CENTER)

global nfc
nfc = customtkinter.CTkLabel(master=uploadImage, text="No File Chosen")

global progresLabel
progressLabel = customtkinter.CTkLabel(master=uploadImage, text="Training...")

icon_img = Image.open("logo.png")
iconPI = ImageTk.PhotoImage(icon_img)
icon = customtkinter.CTkLabel(navigationFrame, text="", image=iconPI)
icon.grid(row=0,column=0,padx=20,pady=20)

fdbutton = customtkinter.CTkButton(master=navigationFrame, text="DETECT FACE", command=lambda : start_webcam(True), text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), fg_color="transparent", height=40)
fdbutton.grid(row=1,column=0,padx=20,pady=10)

frbutton = customtkinter.CTkButton(master=navigationFrame, text="RECOGNIZE FACE", command=lambda: start_webcam(False), text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), fg_color="transparent", height=40)
frbutton.grid(row=2,column=0,padx=20,pady=10)

tbutton = customtkinter.CTkButton(master=navigationFrame, text="ADD NEW FACE", command=lambda : uploadImg(), text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), fg_color="transparent", height=40)
tbutton.grid(row=3,column=0,padx=20,pady=10)

hbutton = customtkinter.CTkButton(master=navigationFrame, text="HOW IT WORKS", command=tutorialpage, text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), fg_color="transparent", height=40)
hbutton.grid(row=4,column=0,padx=20,pady=10)

appearance_mode_menu = customtkinter.CTkOptionMenu(master=navigationFrame, values=["Light", "Dark", "System"], command= change_appearance_mode_event)
appearance_mode_menu.grid(row=6,column=0,padx=20, pady=20, sticky="s")
gc.collect()
root.mainloop()

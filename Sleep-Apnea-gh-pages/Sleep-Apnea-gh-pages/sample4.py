import cv2, time, pandas, winsound, pyttsx3, smtplib,os
from email.message import EmailMessage
from datetime import datetime
import tkinter as tk 
import tkinter.messagebox 
from tkinter import filedialog,Text
import datetime as dt
import os
from PIL import ImageTk,Image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

mainwindow=tk.Tk()
mainwindow.geometry("1000x1000")
mainwindow.resizable(0, 0)
mainwindow.configure(bg='grey')
mainwindow.title("Detection of sleep apnea(ready)")


running =False
# print("starting ", running)

emailentry = tk.StringVar()
patientID = tk.StringVar()
def rec():
    # Assigning our static_background to None 
    global running
    nameee=patientID.get()
    maa = emailentry.get()
    
    running = True
    print("rec ", running)
    static_back = None
    tracker = cv2.legacy_TrackerMOSSE.create()
    # List when any moving object appear or not
    motion_list = [ None, None ] 
    iterations=1 
    current=None
    # Time of movement 
    time = [] 

    # appending frame
    fm=[]  

    # Initializing DataFrame, one column is start time and other column is end time 
    df = pandas.DataFrame(columns = ["Start", "End"]) 
    
    # Capturing video 
    video = cv2.VideoCapture("Test_video.mp4") 

    frm = video.read()[1]
    # img = ImageTk.PhotoImage(Image.fromarray(frm))
    # L1['image'] = img
    # mainwindow.update()
    roi=cv2.selectROI("Tracking",frm)
    cv2.destroyWindow("Tracking")
    # img = ImageTk.PhotoImage(Image.fromarray(roi))
    # L1['image'] = img
    # mainwindow.update()
    tracker.init(frm,roi)
    # Infinite while loop to treat stack of image as video 
    while True:
        
        # Reading frame(image) from video 
        check, frame = video.read()
        frame11 = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame11))
        L1['image'] = img
        mainwindow.update()
        if check==True:
            # Initializing motion = 0(no motion)
            success, r=tracker.update(frame)
            motion = 0
            
            if success:
                frame=frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
                
            else:
                print("The patient moved out of frame")
                #frame=frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

            # Converting color image to gray_scale image
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
            # Converting gray scale image to GaussianBlur, so that change can be find easily 
            gray = cv2.GaussianBlur(gray, (21, 21), 0)  

            # Converting GaussianBlur to canny edge
            edge = cv2.Canny(gray, 34, 34)
            gray = cv2.GaussianBlur(edge, (21, 21), 0)
            
            fm.append(gray)

            # In first iteration we assign the value of static_back to our first frame 
            if static_back is None: 
                static_back = gray
                for i in range(0,16,1):
                    fm.append(gray)
            else:
                static_back=fm[-16]

            # Difference between static background and current frame (which are GaussianBlur frames) 
            try:
                diff_frame = cv2.absdiff(static_back, gray)
            except:
                continue

            # If change in between static background and current frame is greater than 30 it will show white color(255) 
            thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
            thresh_frame = cv2.dilate(thresh_frame, None, iterations = 10)

            # Finding contour of moving object 
            cnts = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            
            for contour in cnts:
                motion = 1
                (x, y, w, h) = cv2.boundingRect(contour) 
                # making green rectangle arround the moving object 
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) 

            if motion==0:
                winsound.Beep(4000,25)
                
                if iterations==1:
                    current=datetime.now().replace(microsecond=0)+dt.timedelta(seconds=10)

                if current==datetime.now().replace(microsecond=0):

                    # voice alert system
                    engine = pyttsx3.init()
                    engine.say("Found no motion. Please check immediately")
                    engine.runAndWait()

                    # mail alert system
                    msg = EmailMessage()
                    mail = smtplib.SMTP('smtp.gmail.com', 587)
                    mail.starttls()
                    mail.login("amrita.researchwork@gmail.com","amrita_research")
                    sub="Motion not detected"
                    body="The patient is not moving. Please check immediately."
                    msg=f'Subject: {sub} \n {body}'
                    
                    mail.sendmail("amrita.researchwork@gmail.com",str(maa), msg)
                    # msg = MIMEMultipart()
                    # msg['From'] = "amrita.researchwork@gmail.com"
                    # msg['To'] = str(maa)
                    # msg['Subject'] = "Motion not detected"
                    # message = "The patient is not moving. Please check immediately."
                    # msg.attach(MIMEText(message,'plain'))
                    # text=msg.as_string()
                    # server=smtplib.SMTP('smtp.gmail.com',587)
                    # server.starttls()
                    # server.login("amrita.researchwork@gmail.com",'amrita_research')
                    # server.sendmail("amrita.researchwork@gmail.com",str(maa),text)
                    # server.quit()
                    # tk.messagebox.showwarning('ALert','check the mail imediately and the the excel sheet created in the current folder you are in for the starttime and endtime of the infant breathing')


                iterations+=1
            else:
                iterations=1

            # Appending status of motion 
            motion_list.append(motion) 
                            
            # Appending Start time of no-motion 
            if motion_list[-1] == 0 and motion_list[-2] == 1: 
                time.append(datetime.now()) 

            # Appending End time of no-motion 
            if motion_list[-1] == 1 and motion_list[-2] == 0: 
                time.append(datetime.now())

            key = cv2.waitKey(30) 
            
            # if q entered whole process will stop 
            # print("rec1 ", running)
            if (running == False):
                # if something is moving then it append the end time of movement 
                if motion == 0: 
                    time.append(datetime.now())
                break

        else:
            print("The video has ended or cannot be converted into frame")
            break


    # Appending time when no-motion is observed in DataFrame 
    for i in range(1, len(time), 2): 
        df = df.append({"Start":time[i], "End":time[i + 1]}, ignore_index = True) 
    
    # Creating a CSV file in which time no-movements occurred will be saved
    
    df.to_csv(str(nameee)+".csv")

    video.release()
    cv2.destroyAllWindows()

def liv():
    # Assigning our static_background to None 
    global running
    nameee=patientID.get()
    maa = emailentry.get()
    
    running = True
    print("rec ", running)
    static_back = None
    tracker = cv2.legacy_TrackerMOSSE.create()
    # List when any moving object appear or not
    motion_list = [ None, None ] 
    iterations=1 
    current=None
    # Time of movement 
    time = [] 

    # appending frame
    fm=[]  

    # Initializing DataFrame, one column is start time and other column is end time 
    df = pandas.DataFrame(columns = ["Start", "End"]) 
    
    # Capturing video 
    video = cv2.VideoCapture(0) 

    frm = video.read()[1]
    # img = ImageTk.PhotoImage(Image.fromarray(frm))
    # L1['image'] = img
    # mainwindow.update()
    roi=cv2.selectROI("Tracking",frm)
    cv2.destroyWindow("Tracking")
    # img = ImageTk.PhotoImage(Image.fromarray(roi))
    # L1['image'] = img
    # mainwindow.update()
    tracker.init(frm,roi)
    # Infinite while loop to treat stack of image as video 
    while True:
        
        # Reading frame(image) from video 
        check, frame = video.read()
        frame11 = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame11))
        L1['image'] = img
        mainwindow.update()
        if check==True:
            # Initializing motion = 0(no motion)
            success, r=tracker.update(frame)
            motion = 0
            
            if success:
                frame=frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
                
            else:
                print("The patient moved out of frame")
                #frame=frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

            # Converting color image to gray_scale image
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
            # Converting gray scale image to GaussianBlur, so that change can be find easily 
            gray = cv2.GaussianBlur(gray, (21, 21), 0)  

            # Converting GaussianBlur to canny edge
            edge = cv2.Canny(gray, 34, 34)
            gray = cv2.GaussianBlur(edge, (21, 21), 0)
            
            fm.append(gray)

            # In first iteration we assign the value of static_back to our first frame 
            if static_back is None: 
                static_back = gray
                for i in range(0,16,1):
                    fm.append(gray)
            else:
                static_back=fm[-16]

            # Difference between static background and current frame (which are GaussianBlur frames) 
            try:
                diff_frame = cv2.absdiff(static_back, gray)
            except:
                continue

            # If change in between static background and current frame is greater than 30 it will show white color(255) 
            thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
            thresh_frame = cv2.dilate(thresh_frame, None, iterations = 10)

            # Finding contour of moving object 
            cnts = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            
            for contour in cnts:
                motion = 1
                (x, y, w, h) = cv2.boundingRect(contour) 
                # making green rectangle arround the moving object 
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) 

            if motion==0:
                winsound.Beep(4000,25)
                
                if iterations==1:
                    current=datetime.now().replace(microsecond=0)+dt.timedelta(seconds=10)

                if current==datetime.now().replace(microsecond=0):

                    # voice alert system
                    engine = pyttsx3.init()
                    engine.say("Found no motion. Please check immediately")
                    engine.runAndWait()

                    # mail alert system
                    msg = EmailMessage()
                    mail = smtplib.SMTP('smtp.gmail.com', 587)
                    mail.starttls()
                    mail.login("amrita.researchwork@gmail.com","amrita_research")
                    sub="Motion not detected"
                    body="The patient is not moving. Please check immediately."
                    msg=f'Subject: {sub} \n {body}'
                    
                    mail.sendmail("amrita.researchwork@gmail.com",str(maa), msg) 
                    tk.messagebox.showwarning('ALert','check the mail imediately and the the excel sheet created in the current folder you are in for the starttime and endtime of the infant breathing')


                iterations+=1
            else:
                iterations=1

            # Appending status of motion 
            motion_list.append(motion) 
                            
            # Appending Start time of no-motion 
            if motion_list[-1] == 0 and motion_list[-2] == 1: 
                time.append(datetime.now()) 

            # Appending End time of no-motion 
            if motion_list[-1] == 1 and motion_list[-2] == 0: 
                time.append(datetime.now())

            key = cv2.waitKey(30) 
            
            # if q entered whole process will stop 
            # print("rec1 ", running)
            if (running == False):
                # if something is moving then it append the end time of movement 
                if motion == 0: 
                    time.append(datetime.now())
                break

        else:
            print("The video has ended or cannot be converted into frame")
            break


    # Appending time when no-motion is observed in DataFrame 
    for i in range(1, len(time), 2): 
        df = df.append({"Start":time[i], "End":time[i + 1]}, ignore_index = True) 
    
    # Creating a CSV file in which time no-movements occurred will be saved
    
    df.to_csv(str(nameee)+".csv")

    video.release()
    cv2.destroyAllWindows()


def stopb():
    global running
    running = False


framet=tk.Frame(mainwindow,bg='grey')
framet.pack(pady=30)

f1 = tk.LabelFrame(mainwindow,width='600',height = '400',bg='grey')
f1.place(x=250,y=150)

L1 = tk.Label(f1,bg='grey')
L1.pack()

livevideo = tk.Button(framet,text = "Live video",font="Timesnewroman 16 bold",command=liv)
livevideo.pack(side = 'left')

recorded = tk.Button(framet,text = "Recorded video",font="Timesnewroman 16 bold",command=rec)
recorded.pack(side = 'left')

stp = tk.Button(framet,text = "Stop video",font="Timesnewroman 16 bold",command=stopb)
stp.pack(side = 'left')



# entryframe = tk.Frame(mainwindow,bg='white',width='10',height='10')
# entryframe.pack()


# elabel = tk.Label(entryframe,text = 'Email')
# elabel.pack(side='left')
# entry1 = tk.Entry(entryframe,textvariable='email',width = 20)
# entry1.pack(side='left')

# plabel = tk.Label(entryframe,text = 'Patient Number')
# plabel.pack(side='left')
# entry2 = tk.Entry(entryframe,textvariable='Patientno',width = 20)
# entry2.pack(side='left')
patientname = tk.StringVar()
phone = tk.StringVar()

def sub():
    data = pandas.DataFrame(columns = ["Name", "Patient ID","Phone Number","Email"]) 
    nameee=patientID.get()
    maa = emailentry.get()
    patiename = patientname.get()
    eeeee = emailentry.get()
    pppp=phone.get()
    data = data.append({"Name":patiename,"Patient ID":nameee,"Phone Number":pppp,"Email":maa},ignore_index=True)
    data.to_csv("patients.csv")
    

pname = tk.Label(mainwindow, text = "Patient Name").place(x = 30,y = 110)  
pname_entry = tk.Entry(pname,textvariable = patientname).place(x=120,y=110)

p = tk.Label(mainwindow, text = "Phone Number").place(x = 30,y = 150)  
p = tk.Entry(p,textvariable = phone).place(x=120,y=150)

name = tk.Label(mainwindow, text = "Patient ID").place(x = 30,y = 190)  
name_entry = tk.Entry(name,textvariable = patientID).place(x=120,y=190)

email = tk.Label(mainwindow, text = "Email").place(x = 30, y = 230)
email_entry = tk.Entry(email,textvariable = emailentry).place(x=120,y=230)  

submit = tk.Button(mainwindow,text= 'Save',command = sub).place(x=30, y = 270)

mainwindow.mainloop()
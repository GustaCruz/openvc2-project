import cv2
import threading
from tkinter import Frame, Label, Tk, PhotoImage, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def switch_to_webcam():
    global webcam_label, map_label, stat_label
    webcam_label.pack()
    map_label.pack_forget()
    stat_label.pack_forget()

def switch_to_map():
    global webcam_label, map_label, stat_label
    webcam_label.pack_forget()
    map_label.pack()
    stat_label.pack_forget()

def switch_to_stat():
    global webcam_label, map_label, stat_label
    webcam_label.pack_forget()
    map_label.pack_forget()
    stat_label.pack()

def show_webcam():
    global webcam_label
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (580, 350))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            webcam_label.configure(image=imgtk)
            webcam_label.image = imgtk
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()

root = ctk.CTk()
root.geometry("800x450")
root.title("Drone System")

frame = ctk.CTkFrame(master=root)
frame.pack(pady=10, padx=6, fill="both", expand=False)

label = ctk.CTkLabel(master=frame, text="Drone System", font=("Roboto", 14), height=0)
label.pack(pady=1, padx=10, side="top", anchor="n")

main_frame = Frame(master=frame, width=500, height=350, background="black")  
main_frame.pack(pady=1, padx=8, side="right", anchor="ne")

webcam_label = Label(main_frame)

# Load the map image
map_image = Image.open("C:\\Users\\Gamar\\Pictures\\map.png")
map_image = map_image.resize((500, 350), Image.ANTIALIAS)
map_photo = ImageTk.PhotoImage(map_image)

map_label = Label(main_frame, image=map_photo)

# Load the stat image
stat_image = Image.open("C:\\Users\\Gamar\\Pictures\\stat.png")
stat_image = stat_image.resize((680, 350), Image.ANTIALIAS)
stat_photo = ImageTk.PhotoImage(stat_image)

stat_label = Label(main_frame, image=stat_photo)

# Create side_sc frames
side_sc1 = ctk.CTkFrame(master=frame)  
side_sc1.pack(pady=4, padx=8, side="top", anchor="nw")
text_label1 = ctk.CTkLabel(master=side_sc1, text="MAIN", font=("Roboto", 12), width=80, anchor="center")
text_label1.pack(pady=4, padx=8, side="top", anchor="nw")
text_label1.bind("<Button-1>", lambda event: switch_to_webcam())

side_sc2 = ctk.CTkFrame(master=frame)  
side_sc2.pack(pady=4, padx=8, side="top", anchor="nw")  
text_label2 = ctk.CTkLabel(master=side_sc2, text=" MAP", font=("Roboto", 12), width=80, anchor="center")
text_label2.pack(pady=4, padx=8, side="top", anchor="nw")
text_label2.bind("<Button-1>", lambda event: switch_to_map())

side_sc3 = ctk.CTkFrame(master=frame)  
side_sc3.pack(pady=4, padx=8, side="top", anchor="nw")
text_label3 = ctk.CTkLabel(master=side_sc3, text="STAT", font=("Roboto", 12), width=80, anchor="center")
text_label3.pack(pady=4, padx=8, side="top", anchor="nw")
text_label3.bind("<Button-1>", lambda event: switch_to_stat())

side_sc4 = ctk.CTkFrame(master=frame)  
side_sc4.pack(pady=4, padx=8, side="top", anchor="nw")  
text_label4 = ctk.CTkLabel(master=side_sc4, text="SNAP", font=("Roboto", 12), width=80, anchor="center")
text_label4.pack(pady=4, padx=8, side="top", anchor="nw")

side_sc5 = ctk.CTkFrame(master=frame)  
side_sc5.pack(pady=4, padx=8, side="top", anchor="nw")
text_label5 = ctk.CTkLabel(master=side_sc5, text="SETT", font=("Roboto", 12), width=80, anchor="center")
text_label5.pack(pady=4, padx=8, side="top", anchor="nw") 

side_sc6 = ctk.CTkFrame(master=frame)  
side_sc6.pack(pady=6, padx=8, side="top", anchor="nw")
text_label6 = ctk.CTkLabel(master=side_sc6, text="QUIT", font=("Roboto", 12), width=80, anchor="center")
text_label6.pack(pady=4, padx=8, side="top", anchor="nw")

thread = threading.Thread(target=show_webcam)
thread.daemon = True
thread.start()

root.mainloop()

#########################################################################
#                      UCHL - Senior Project                            #
#                                                                       #
#   Team: Spatial Positioning, Observation, and Tracking System (SPOTS) #
#                                                                       #
#   Memebers: Gustavo, Nicole, Drew, Diego, Ricardo                     #
#                                                                       #
#   Goal:                                                               #
#                                                                       #
#   Notes:  UI Version 3: MAIN, MAP, STAT, QUIT are working             #
#   Link: https://github.com/GustaCruz/openvc2-project/                 #
#                                                                       #
#########################################################################
# pip install opencv-python customtkinter tkintermapview geopy requests tk adafruit-circuitpython-rfm69 RPi.GPIO weatherapi pyDatalog sqlalchemy image pillow

import cv2
import threading
import datetime
import customtkinter as ctk
from tkinter import Frame, Label, Tk
from PIL import Image, ImageTk, ImageGrab
from tkintermapview import TkinterMapView
from geopy.distance import geodesic
import board
import busio
import digitalio
import adafruit_rfm69
import adafruit_gps
import pingCalculation
import RPi.GPIO as GPIO
import serial
import os


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

#Global varaibles to store pilot/drone positional data
droneCoords = [None, None]
pilotCoords = [None, None]
altitude = None
servoAng = None
droneHeading = None

button1 = 26
button2 = 19

uart = serial.Serial("/dev/serial0", baudrate=9600,timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D25)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
prev_press = {button1: False, button2: False}

# Servo data
servoAng = 50.00

# Packet processing functions
def split_packet(packet_text):
    values = packet_text.split("+")
    if len(values) == 6:
        return values
    else:
        print("Packet is corrupted, discarding")
        #global missedPKT
        #missedPKT += 1
        return [None] * 6

def send_control_data(servo_angle):
    controlData = f"{servo_angle}"
    rfm69.send(bytes(controlData, "utf-8"))
    print(f"Sending Packet: {controlData}\n")

def receive_packet():
    packet = rfm69.receive(timeout=0.1)
    if packet is None:
        return None
    try:
        packet_text = packet.decode('utf-8')
        return packet_text
    except UnicodeDecodeError:
        return None

def handle_buttons():
    global servoAng, prev_press
    button1_pressed = not GPIO.input(button1)
    button2_pressed = not GPIO.input(button2)
    
    if button1_pressed != prev_press[button1]:
        if button1_pressed:
            servoAng = min(90.00, servoAng + 10.00)
    if button2_pressed != prev_press[button2]:
        if button2_pressed:
            servoAng = max(0.00, servoAng - 10.00)
        
def get_gps_data():
    """ Retrieve GPS data. """
    gps.update()
    if gps.has_fix:
        pilotCoords[0] = round(gps.latitude, 5)
        pilotCoords[1] = round(gps.longitude, 5)
    else:
        #return 'NF', 'NF'
        pilotCoords[0] = '29.47649'
        pilotCoords[1] = '-95.22658'


class App(ctk.CTk):
    APP_NAME = "SPOTS Pilot System"
    # GENRAL APP SIZE ==============================================
    WIDTH = 800
    HEIGHT = 450

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.marker_list = []
        self.init_ui()
        self.start_webcam_thread()

    def init_ui(self):
        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=10, padx=6, fill="both", expand=True)

        self.label = ctk.CTkLabel(master=self.frame, text="Drone System", font=("Roboto", 14), height=0)
        self.label.pack(pady=1, padx=10, side="top", anchor="n")

        self.main_frame = Frame(master=self.frame, width=500, height=380, background="black")
        self.main_frame.pack(pady=1, padx=8, side="top", anchor="ne", fill="both", expand=True)

        self.webcam_label = Label(self.main_frame)
        self.webcam_label.pack()
        
# MAP STARTING POINT ==============================================================================

        self.map_widget = TkinterMapView(self.main_frame, corner_radius=0, width=790, height=390)
        if pilotCoords[0] is not None:
            self.map_widget.set_position(pilotCoords[0], pilotCoords[1])
        else:
            self.map_widget.set_position(29.5783681, -95.1041635)
        self.map_widget.set_zoom(16)
        self.map_widget.place_forget()
        
# MAP APP SIZE ====================================================================================

        self.map_controls_frame = ctk.CTkFrame(master=self.main_frame, width=150, height=220, corner_radius=0, fg_color=None)
        self.map_controls_frame.place_forget()
        self.create_map_controls()
        self.create_nav_buttons()
        
# MAP CONTROLS FOR MAP TAB (MARKERS, BUTTONS, DISTANCE CALCULATIONS) ==============================

    def create_map_controls(self):
        self.label_marker1 = ctk.CTkLabel(master=self.map_controls_frame, text="Pilot Coords:", anchor="w")
        self.label_marker1.pack(pady=(2, 0), padx=(1, 10))
        self.entry_marker1 = ctk.CTkEntry(master=self.map_controls_frame, placeholder_text="Your coords...")
        self.entry_marker1.pack(pady=(2, 0), padx=(10, 10))
        self.button_add_marker1 = ctk.CTkButton(master=self.map_controls_frame, text="Find your location", command=self.add_marker1_event)
        self.button_add_marker1.pack(pady=(1, 5), padx=(10, 10))

        self.label_marker2 = ctk.CTkLabel(master=self.map_controls_frame, text="Marker 2:", anchor="w")
        self.label_marker2.pack(pady=(5, 0), padx=(10, 10))
        self.entry_marker2 = ctk.CTkEntry(master=self.map_controls_frame, placeholder_text="Paste your coords...")
        self.entry_marker2.pack(pady=(5, 0), padx=(10, 10))
        self.button_add_marker2 = ctk.CTkButton(master=self.map_controls_frame, text="Add Marker 2", command=self.add_marker2_event)
        self.button_add_marker2.pack(pady=(1, 10), padx=(10, 10))

        self.button_clear_markers = ctk.CTkButton(master=self.map_controls_frame, text="Clear Markers", command=self.clear_marker_event)
        self.button_clear_markers.pack(pady=(5, 10), padx=(10, 10))

        self.map_label = ctk.CTkLabel(self.map_controls_frame, text="Tile Server:", anchor="w")
        self.map_label.pack(pady=(1, 0), padx=(10, 10))
        self.map_option_menu = ctk.CTkOptionMenu(self.map_controls_frame, values=["OpenStreetMap", "Google normal", "Google satellite"], command=self.change_map)
        self.map_option_menu.pack(pady=(1, 5), padx=(10, 10))
        self.distance_label = ctk.CTkLabel(self.map_controls_frame, text="Distance: ", anchor="w")
        self.distance_label.pack(pady=(5, 35), padx=(10, 10))
        self.map_option_menu.set("OpenStreetMap")
        
 # GRABBING CORDS FOR THE MAP WIDGET CAN BE TURNED INTO AN AUTO FUNCTION ===========================
 
    def add_marker1_event(self):
        coords = pilotCoords
        if coords[0] is not None:
            if len(coords) == 2:
                self.add_marker(1, float(coords[0]), float(coords[1]))
                self.map_widget.set_position(float(coords[0]), float(coords[1]))

    def add_marker2_event(self):
        #hardcoding values
        altitude = 10.00
        servoAng = 85.00
        droneCoords[0] = '29.4757615'
        droneCoords[1] = '-95.2245415'
        droneHeading = '180.00'
        
        if altitude is not None:
            base = pingCalculation.calculate_base(float(altitude), float(servoAng))
            coords = pingCalculation.calculate_new_coordinates(float(droneCoords[0]), float(droneCoords[1]), float(droneHeading), base)
            pingLat = float(coords[0])
            pingLon = float(coords[1])
            
            print("Pilot Coords: ", pilotCoords[0], ", ", pilotCoords[1])
            print("Drone Coords: ", droneCoords[0], ", ", droneCoords[1])
            print("Calculated Coords: ", coords[0], ", ", coords[1])
            if len(coords) == 2:
                self.add_marker(2, pingLat, pingLon)

    def add_marker(self, marker_number, lat, lon):
        if marker_number == 1:
            if lat is not None:
                marker = self.map_widget.set_marker(lat, lon, text=f"Pilot")
        else:
            if lat is not None:
                marker = self.map_widget.set_marker(lat, lon, text=f"Ping")
            
        self.marker_list.append(marker)
        if len(self.marker_list) == 2:
            self.calculate_distance()

    def clear_marker_event(self):
        self.map_widget.delete_all_marker()
        self.marker_list.clear()
        self.distance_label.configure(text="Distance: ")
        
# DISTANCE CALCS ===================================================================================

    def calculate_distance(self):
        if len(self.marker_list) == 2:
            coords_1 = self.marker_list[0].position
            coords_2 = self.marker_list[1].position
            distance = geodesic(coords_1, coords_2).meters
            self.distance_label.configure(text=f"Distance: {distance:.2f} meters")

    def change_map(self, map_type):
        tile_servers = {
            "OpenStreetMap": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "Google normal": "https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}",
            "Google satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        }
        self.map_widget.set_tile_server(tile_servers[map_type]) 
        
# NAVAGATIONAL BUTTONS CAN BE ADJUSTED =============================================================

    def create_nav_buttons(self):
        self.nav_buttons_frame = ctk.CTkFrame(master=self.frame, height=50, corner_radius=0)
        self.nav_buttons_frame.pack(side="bottom", fill="x")

        for btn_text, command in [("MAIN", self.switch_to_webcam), ("MAP", self.switch_to_map), 
                                  ("STAT", self.switch_to_stat), ("SNAP", self.take_screenshot), 
                                  ("SETT", self.switch_to_sett), ("QUIT", self.on_closing)]:
            self.create_nav_button(btn_text, command)

    def create_nav_button(self, text, command):
        button = ctk.CTkButton(master=self.nav_buttons_frame, text=text, command=command, width=70, height=30)
        button.pack(side="left", padx=6, pady=4)

# SCREENSHOT OF UI ============================================================

    def take_screenshot(self):
        # Capture the current screen
        screenshot = ImageGrab.grab()

        # Save the screenshot with a timestamp in the filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot.save(f"screenshot_{timestamp}.png")

        print(f"Screenshot saved as screenshot_{timestamp}.png")

# WEBCAM SETUP ====================================================================================

    def start_webcam_thread(self):
        self.thread = threading.Thread(target=self.show_webcam)
        self.thread.daemon = True
        self.thread.start()

    def show_webcam(self):
        cap = cv2.VideoCapture(0) # CHANGE VALUE IF WEBCAM IS NOT SHOWING ==============
        while cap.isOpened():
            global servoAng, altitude, droneHeading
            handle_buttons()
            get_gps_data()
            send_control_data(servoAng)
            
            #receive packet
            packet_text = receive_packet()
            #check if empty
            if packet_text:
                #split data into array of values
                altStr, droneCoords[0], droneCoords[1], angStr, dPressureStr, droneHeading = split_packet(packet_text)
                
                #hardcoded heading values (north)
                droneHeading = '360'
                #check if array is occupied
                if altStr is not None:
                    altitude = float(altStr)
                    servoAng = float(angStr)
                    
                    print("Drone Alt: " ,altStr)
                    print("Drone Lat:" ,droneCoords[0])
                    print("Drone Lon " , droneCoords[1])
                    print("Servo Ang: ", angStr)
                    print("Drone Heading", droneHeading)
                    
            print("Pilot Lat: ", pilotCoords[0])
            print("Pilot Lon: ", pilotCoords[1])
            ret, frame = cap.read()
            if ret: # CROSSHAIR ========================================================
                height, width, _ = frame.shape
                cv2.line(frame, (width // 2 - 8, height // 2), (width // 2 + 8, height // 2), (0, 255, 0), 2)
                cv2.line(frame, (width // 2, height // 2 - 8), (width // 2, height // 2 + 8), (0, 255, 0), 2)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (580, 350))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.webcam_label.configure(image=imgtk)
                self.webcam_label.image = imgtk
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
        
#  TOGGLE SWITCHING BETWEEN DIFFERENT SCREENS IN THE UI ===========================================

    def switch_to_webcam(self):
        self.map_widget.place_forget()
        self.map_controls_frame.place_forget()
        self.webcam_label.pack()

    def switch_to_map(self):
        self.webcam_label.pack_forget()
        self.map_controls_frame.place(x=0, y=0)
        self.map_widget.place(x=0, y=0)

    def switch_to_stat(self):
        self.webcam_label.pack_forget()
        self.map_widget.place_forget()
        self.map_controls_frame.place_forget()

    def switch_to_sett(self):
        self.webcam_label.pack_forget()
        self.map_widget.place_forget()
        self.map_controls_frame.place_forget()

    def on_closing(self):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()            
        

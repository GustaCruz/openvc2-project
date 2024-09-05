import cv2
import threading
from tkinter import Frame, Label, Tk
from PIL import Image, ImageTk
import customtkinter as ctk
from tkintermapview import TkinterMapView
from geopy.distance import geodesic
import requests
from datetime import datetime, timedelta

# pip installs below VVV
# pip install opencv-python customtkinter tkintermapview geopy requests tk

# Set CustomTkinter appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Weather API details
WEATHER_API_KEY = '02b935eac0203a67b8713c5ea109688c'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
FORECAST_API_URL = 'https://api.openweathermap.org/data/2.5/forecast'

# Main Application Class
class App(ctk.CTk):

    APP_NAME = "Drone System with Map Integration"
    WIDTH = 800
    HEIGHT = 450
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.marker_list = []

        # Create main frame
        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=10, padx=6, fill="both", expand=True)

        self.label = ctk.CTkLabel(master=self.frame, text="Drone System", font=("Roboto", 14), height=0)
        self.label.pack(pady=1, padx=10, side="top", anchor="n")

        # Main frame for webcam and map
        self.main_frame = Frame(master=self.frame, width=500, height=350, background="black")
        self.main_frame.pack(pady=1, padx=8, side="top", anchor="ne", fill="both", expand=True)

        self.webcam_label = Label(self.main_frame)

        # Initialize map widget
        self.map_widget = TkinterMapView(self.main_frame, corner_radius=0, width=620, height=220)
        self.map_widget.set_position(29.5783681, -95.1041635)  # Example coordinates
        self.map_widget.set_zoom(16)
        self.map_widget.grid(row=0, column=1, sticky="nsew")
        self.map_widget.grid_remove()  # Hide the map initially

        # Frame for map controls
        self.map_controls_frame = ctk.CTkFrame(master=self.main_frame, width=150, height=220, corner_radius=0, fg_color=None)
        self.map_controls_frame.grid(row=0, column=0, sticky="nsew")
        self.map_controls_frame.grid_remove()  # Hide the controls initially

        self.label_marker1 = ctk.CTkLabel(master=self.map_controls_frame, text="Marker 1:", anchor="w")
        self.label_marker1.pack(pady=(2, 0), padx=(1, 10))
        self.entry_marker1 = ctk.CTkEntry(master=self.map_controls_frame, placeholder_text="Paste your coords...")
        self.entry_marker1.pack(pady=(2, 0), padx=(10, 10))
        self.button_add_marker1 = ctk.CTkButton(master=self.map_controls_frame, text="Add Marker 1", command=self.add_marker1_event)
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

        # Create navigation buttons at the bottom
        self.nav_buttons_frame = ctk.CTkFrame(master=self.frame, height=50, corner_radius=0)
        self.nav_buttons_frame.pack(side="bottom", fill="x")

        # Create buttons with padding between them
        self.create_nav_button("MAIN", self.switch_to_webcam)
        self.create_nav_button("MAP", self.switch_to_map)
        self.create_nav_button("STAT", self.switch_to_stat)
        self.create_nav_button("SNAP", lambda: print("SNAP clicked"))
        self.create_nav_button("SETT", lambda: print("SETT clicked"))
        self.create_nav_button("QUIT", self.on_closing)

        # Initialize weather frame
        self.weather_frame = None
        self.weather_label = None

        # Start webcam thread
        self.thread = threading.Thread(target=self.show_webcam)
        self.thread.daemon = True
        self.thread.start()

    def create_nav_button(self, text, command):
        button = ctk.CTkButton(
            master=self.nav_buttons_frame, 
            text=text, 
            command=command,
            width=80,  # Set a fixed width for the buttons
            height=30  # Optionally, set a fixed height
        )
        button.pack(side="left", padx=6, pady=4)  # Increased padding

    def switch_to_webcam(self):
        self.webcam_label.pack()
        self.map_widget.grid_remove()
        self.map_controls_frame.grid_remove()
        if self.weather_frame:
            self.weather_frame.pack_forget()

    def switch_to_map(self):
        self.webcam_label.pack_forget()
        self.map_controls_frame.grid()
        self.map_widget.grid()
        if self.weather_frame:
            self.weather_frame.pack_forget()

    def switch_to_stat(self):
        self.webcam_label.pack_forget()
        self.map_widget.grid_remove()
        self.map_controls_frame.grid_remove()
        if not self.weather_frame:
            self.weather_frame = ctk.CTkFrame(master=self.frame, height=300)
            self.weather_frame.pack(pady=10, padx=10, fill="both", expand=True)
            
            self.weather_label = ctk.CTkLabel(self.weather_frame, text="Weather Information", font=("Roboto", 14))
            self.weather_label.pack(pady=5)

            self.weather_info_label = ctk.CTkLabel(self.weather_frame, text="", font=("Roboto", 12))
            self.weather_info_label.pack(pady=5)

            self.forecast_frame = ctk.CTkFrame(master=self.weather_frame)
            self.forecast_frame.pack(pady=5, padx=5, fill="both", expand=True)

            self.forecast_label = ctk.CTkLabel(self.forecast_frame, text="3-Day Forecast", font=("Roboto", 14))
            self.forecast_label.pack(pady=5)

            self.forecast_info_label = ctk.CTkLabel(self.forecast_frame, text="", font=("Roboto", 12), anchor="w")
            self.forecast_info_label.pack(pady=5, anchor="w")

        self.show_weather_info()
        self.show_forecast_info()
        self.main_frame.pack_forget()  # Remove the black box

    def show_webcam(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (580, 350))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.webcam_label.configure(image=imgtk)
                self.webcam_label.image = imgtk
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()

    def add_marker1_event(self):
        coords = self.entry_marker1.get().strip().split()
        if len(coords) == 2:
            lat, lon = coords
            self.add_marker(1, float(lat), float(lon))

    def add_marker2_event(self):
        coords = self.entry_marker2.get().strip().split()
        if len(coords) == 2:
            lat, lon = coords
            self.add_marker(2, float(lat), float(lon))

    def add_marker(self, marker_number, lat, lon):
        marker = self.map_widget.set_marker(lat, lon, text=f"Marker {marker_number}")
        self.marker_list.append(marker)
        if len(self.marker_list) == 2:
            self.calculate_distance()

    def clear_marker_event(self):
        self.map_widget.delete_all_marker()
        self.marker_list.clear()
        self.distance_label.configure(text="Distance: ")

    def calculate_distance(self):
        if len(self.marker_list) == 2:
            coords_1 = (self.marker_list[0].position[0], self.marker_list[0].position[1])
            coords_2 = (self.marker_list[1].position[0], self.marker_list[1].position[1])
            distance = geodesic(coords_1, coords_2).meters
            self.distance_label.configure(text=f"Distance: {distance:.2f} meters")

    def show_weather_info(self):
        if self.weather_frame and self.weather_label and self.weather_info_label:
            # Use Houston, US as a default location
            location = "Houston, US"

            # Fetch weather details from OpenWeatherMap
            weather_data = self.get_weather()
            if weather_data:
                weather_description = weather_data.get('weather', [{}])[0].get('description', 'No data')
                temperature = weather_data.get('main', {}).get('temp', 'No data')
                temperature = round(temperature * 9/5 + 32, 2)  # Convert to Fahrenheit
                self.weather_info_label.configure(text=f"Weather in {location}: {weather_description.capitalize()}, Temp: {temperature}°F")
            else:
                self.weather_info_label.configure(text="Weather: Data not available")

    def show_forecast_info(self):
        if self.forecast_info_label:
            # Fetch forecast details from OpenWeatherMap
            forecast_data = self.get_weather_forecast()
            if forecast_data:
                forecast_text = ""
                for entry in forecast_data.get('list', [])[:3]:  # Only take the next 3 days' forecast
                    dt = datetime.fromtimestamp(entry.get('dt', 0))
                    date_str = dt.strftime("%B %d, %I:%M %p")  # Format: Month day, 12 hr format
                    temp = round(entry.get('main', {}).get('temp', 0) * 9/5 + 32, 2)  # Convert to Fahrenheit
                    forecast_text += f"{date_str}: {temp}°F\n"
                self.forecast_info_label.configure(text=forecast_text.strip())
            else:
                self.forecast_info_label.configure(text="Forecast: Data not available")

    def get_weather(self):
        try:
            # Fetch weather data for Houston
            response = requests.get(WEATHER_API_URL, params={
                'q': 'Houston,US',
                'appid': WEATHER_API_KEY,
                'units': 'metric'  # Celsius
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_weather_forecast(self):
        try:
            # Fetch 3-day forecast data for Houston
            response = requests.get(FORECAST_API_URL, params={
                'q': 'Houston,US',
                'appid': WEATHER_API_KEY,
                'units': 'metric',  # Celsius
                'cnt': 24  # Number of data points (3-hour intervals for 3 days)
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching forecast data: {e}")
            return None

    def change_map(self, map_type):
        if map_type == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif map_type == "Google normal":
            self.map_widget.set_tile_server("https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}")
        elif map_type == "Google satellite":
            self.map_widget.set_tile_server("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}")

    def on_closing(self):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()


import customtkinter
from tkintermapview import TkinterMapView
from geopy.distance import geodesic

customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):

    APP_NAME = "TkinterMapView with CustomTkinter"
    WIDTH = 650
    HEIGHT = 400
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=20, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(12, weight=1)

        self.label_marker1 = customtkinter.CTkLabel(master=self.frame_left, text="", anchor="n", width=20)
        self.label_marker1.grid(row=0, column=0, padx=1, pady=0)
        self.entry_marker1 = customtkinter.CTkEntry(master=self.frame_left,
                                                     placeholder_text="Paste your coords...")
        self.entry_marker1.grid(row=0, column=0, padx=2, pady=(5, 0))
        self.button_add_marker1 = customtkinter.CTkButton(master=self.frame_left,
                                                           text="Add Marker 1",
                                                           command=self.add_marker1_event)
        self.button_add_marker1.grid(row=1, column=0, padx=1, pady=(0, 0))  # Adjusted pady here



        self.label_marker2 = customtkinter.CTkLabel(master=self.frame_left, text="", anchor="n")
        self.label_marker2.grid(row=2, column=0, padx=1, pady=0)
        self.entry_marker2 = customtkinter.CTkEntry(master=self.frame_left,
                                                     placeholder_text="Paste your coords...")
        self.entry_marker2.grid(row=3, column=0, padx=(20, 20), pady=(0, 0))
        self.button_add_marker2 = customtkinter.CTkButton(master=self.frame_left,
                                                           text="Add Marker 2",
                                                           command=self.add_marker2_event)
        self.button_add_marker2.grid(row=4, column=0, padx=(20, 20), pady=(0, 0))  # Adjusted pady here



        self.button_clear_markers = customtkinter.CTkButton(master=self.frame_left,
                                                            text="Clear Markers",
                                                            command=self.clear_marker_event)
        self.button_clear_markers.grid(row=5, column=0, padx=(20, 20), pady=(10, 0))

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=6, column=0, padx=(20, 20), pady=(10, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                            values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                            command=self.change_map)
        self.map_option_menu.grid(row=7, column=0, padx=(20, 20), pady=(0, 10))

        # Add label to display distance
        self.distance_label = customtkinter.CTkLabel(self.frame_left, text="Distance:", anchor="w", width=50)
        self.distance_label.grid(row=8, column=0, padx=(20, 20), pady=(0, 10))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_search = customtkinter.CTkButton(master=self.frame_right,
                                                      text="Search",
                                                      width=90,
                                                      command=self.search_event)
        self.button_search.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=1)

        # Set default values
        self.map_widget.set_address("University of Houston - Clear Lake")
        self.map_option_menu.set("OpenStreetMap")

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

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

    def add_marker(self, marker_num, lat, lon):
        # If there are already two markers, remove the first one
        if len(self.marker_list) >= 2:
            self.marker_list.pop(0).delete()
        # Set the marker on the map
        text = "Marker " + str(marker_num)
        marker = self.map_widget.set_marker(lat, lon, text=text)
        self.marker_list.append(marker)

        # If both markers are present, calculate and display distance
        if len(self.marker_list) == 2:
            marker1 = self.marker_list[0].position
            marker2 = self.marker_list[1].position
            distance_meters = geodesic(marker1, marker2).meters
            distance_km = geodesic(marker1, marker2).kilometers
            distance_text = f"{distance_meters:.4f} meters\n{distance_km:.4f} km"
            self.distance_label.configure(text=distance_text)

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()
        self.marker_list.clear()

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                             max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                             max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()

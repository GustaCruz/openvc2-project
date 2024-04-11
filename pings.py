import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import requests
import io
from geopy.distance import geodesic

API_KEY = 'API key'

def calculate_distance(latitude1, longitude1, latitude2, longitude2):
    coords_1 = (latitude1, longitude1)
    coords_2 = (latitude2, longitude2)
    return geodesic(coords_1, coords_2).meters

def update_map():
    latitude1 = entry_lat1.get()
    longitude1 = entry_long1.get()
    latitude2 = entry_lat2.get()
    longitude2 = entry_long2.get()
    zoom = entry_zoom.get()

    try:
        latitude1 = float(latitude1)
        longitude1 = float(longitude1)
        latitude2 = float(latitude2)
        longitude2 = float(longitude2)

        zoom = max(0, min(int(zoom), 21))


        center_lat = (latitude1 + latitude2) / 2
        center_long = (longitude1 + longitude2) / 2

        url = f"https://maps.googleapis.com/maps/api/staticmap?center={center_lat},{center_long}&zoom={zoom}&size=400x400&maptype=satellite&markers=color:red%7Clabel:O%7C{latitude1},{longitude1}&markers=color:red%7Clabel:P%7C{latitude2},{longitude2}&path=color:0x0000ff|weight:5|{latitude1},{longitude1}|{latitude2},{longitude2}&key={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  
        image_data = response.content

        map_image = Image.open(io.BytesIO(image_data))
        map_image = map_image.resize((400, 400), Image.LANCZOS)  

        distance = calculate_distance(latitude1, longitude1, latitude2, longitude2)

        draw = ImageDraw.Draw(map_image)
        draw.text((320, 370), f"Distance: {distance:.2f} meters", fill="red")

        map_photo = ImageTk.PhotoImage(map_image)
        label_map.configure(image=map_photo)
        label_map.image = map_photo

        window.update_idletasks()
    except (requests.exceptions.RequestException, ValueError) as e:
        print("Error fetching map:", e)
        label_map.config(text="Error fetching map")

window = tk.Tk()
window.title("Static Map Generator")

label_lat1 = tk.Label(window, text="Latitude 1:")
label_lat1.pack()
entry_lat1 = tk.Entry(window)
entry_lat1.pack()

label_long1 = tk.Label(window, text="Longitude 1:")
label_long1.pack()
entry_long1 = tk.Entry(window)
entry_long1.pack()

label_lat2 = tk.Label(window, text="Latitude 2:")
label_lat2.pack()
entry_lat2 = tk.Entry(window)
entry_lat2.pack()

label_long2 = tk.Label(window, text="Longitude 2:")
label_long2.pack()
entry_long2 = tk.Entry(window)
entry_long2.pack()

label_zoom = tk.Label(window, text="Zoom Level:")
label_zoom.pack()
entry_zoom = tk.Entry(window)
entry_zoom.pack()

btn_update = tk.Button(window, text="Update Map", command=update_map)
btn_update.pack()

label_map = tk.Label(window)
label_map.pack()

window.mainloop()

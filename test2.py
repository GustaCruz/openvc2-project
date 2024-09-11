import time
import board
import busio
import adafruit_gps
import requests

class GPSDataHandler:
    def __init__(self):
        self.latitude = None
        self.longitude = None
    
    def update_gps_data(self, data):
        self.latitude = data['lat']
        self.longitude = data['long']

def read_gps_data(output):
    import serial
    uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
    
    gps = adafruit_gps.GPS(uart, debug=False) # Use UART/pyserial

    # sending message configuration commands to GPS
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")
    last_print = time.monotonic()
    
    while True:
        # setting zero values for lat/lon
        latitude = 0
        longitude = 0

        # update gps and read in lat/lon values
        gps.update()
        latitude = gps.latitude
        longitude = gps.longitude

        output.update_gps_data({'lat' : latitude, 'long' : longitude})
        time.sleep(60)  # Sleep for 60 seconds before updating again

def get_zip_code(lat, lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        results = data['results']
        for result in results:
            for component in result['address_components']:
                if 'postal_code' in component['types']:
                    return component['long_name']
        return "ZIP code not found"
    else:
        return "Failed to retrieve data"

def get_pressure(city_name, api_key):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city_name}"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        pressure_mb = data["current"]["pressure_mb"]
        return pressure_mb
    else:
        print("Failed to fetch weather data.")
        return None

def main():
    google_maps_api_key = "API key"
    weather_api_key = "API key"
    
    # Create an instance of GPSDataHandler
    gps_data_handler = GPSDataHandler()
    
    # Start reading GPS data in a separate thread
    import threading
    gps_thread = threading.Thread(target=read_gps_data, args=(gps_data_handler,))
    gps_thread.start()
    
    while True:
        if gps_data_handler.latitude is not None and gps_data_handler.longitude is not None:
            # Get ZIP code from coordinates
            zip_code = get_zip_code(gps_data_handler.latitude, gps_data_handler.longitude, google_maps_api_key)
            
            # Use ZIP code as the city for weather data
            pressure = get_pressure(zip_code, weather_api_key)
            
            if pressure is not None:
                print(f"Atmospheric Pressure in {zip_code}: {pressure} mb")
            else:
                print("Weather data not available.")
            time.sleep(60)  # Update pressure every minute

if __name__ == "__main__":
    main()
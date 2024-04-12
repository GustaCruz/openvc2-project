import time
import board
import busio
import adafruit_gps
import serial
import requests

def read_gps_data(output):
    uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
    gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial

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

        output.update_gps_data({'lat': latitude, 'long': longitude})
        time.sleep(1)  # Optional delay to control update frequency

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

def get_pressure(lat, lng, google_maps_api_key, weather_api_key):
    zip_code = get_zip_code(lat, lng, google_maps_api_key)
    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={zip_code}"
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

    class OutputHandler:
        def update_gps_data(self, data):
            lat = data['lat']
            lng = data['long']
            pressure = get_pressure(lat, lng, google_maps_api_key, weather_api_key)
            if pressure is not None:
                print(f"Atmospheric Pressure at {lat}, {lng}: {pressure} mb")
            else:
                print("Weather data not available.")

    output = OutputHandler()
    read_gps_data(output)

if __name__ == "__main__":
    main()

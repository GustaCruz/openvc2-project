import requests

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
    
    # Input coordinates
    lat = input("Enter latitude: ")
    lng = input("Enter longitude: ")
    
    # Get ZIP code from coordinates
    zip_code = get_zip_code(lat, lng, google_maps_api_key)
    
    # Use ZIP code as the city for weather data
    pressure = get_pressure(zip_code, weather_api_key)
    
    if pressure is not None:
        print(f"Atmospheric Pressure in {zip_code}: {pressure} mb")
    else:
        print("Weather data not available.")

if __name__ == "__main__":
    main()

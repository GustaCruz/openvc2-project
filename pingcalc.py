import math

def calculate_base(altitude, servo_degrees):

    # Convert the servo angle from degrees to radians
    servo_radians = math.radians(servo_degrees)
    
    # Calculate the base length using the tangent function
    base = altitude * math.tan(servo_radians)
    
    return base

def calculate_new_coordinates(drone_lat, drone_lon, heading, base):

    # Radius of the Earth in meters
    R = 6371000
    
    # Convert latitude, longitude, and heading from degrees to radians
    drone_lat_rad = math.radians(drone_lat)
    drone_lon_rad = math.radians(drone_lon)
    heading_rad = math.radians(heading)

    # Calculate the new latitude using the spherical law of cosines
    ping_lat_rad = math.asin(math.sin(drone_lat_rad) * math.cos(base / R) +
                            math.cos(drone_lat_rad) * math.sin(base / R) * math.cos(heading_rad))
    
    # Calculate the new longitude
    ping_lon_rad = drone_lon_rad + math.atan2(math.sin(heading_rad) * math.sin(base / R) * math.cos(drone_lat_rad),
                                              math.cos(base / R) - math.sin(drone_lat_rad) * math.sin(ping_lat_rad))
    
    # Convert the new latitude and longitude from radians to degrees
    ping_latitude = math.degrees(ping_lat_rad)
    ping_longitude = math.degrees(ping_lon_rad)
    
    return ping_latitude, ping_longitude

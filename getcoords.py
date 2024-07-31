# importing modules
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

def get_coords(city_name):
    try:
        geoLoc = Nominatim(user_agent="GetLoc")
        location = geoLoc.geocode(city_name)
        if location:
            return (location.latitude, location.longitude)
        else:
            return "City not found"
    except GeopyError as e:
        return f"Error: {e}"

# Example usage
coords = get_coords("Cambridge, US")
print(coords)

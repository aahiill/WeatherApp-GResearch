# importing modules
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

def get_city(lat, long):
    try:
        geoLoc = Nominatim(user_agent="GetLoc")
        locname = geoLoc.reverse((lat, long), addressdetails=True)
        address = locname.raw['address']
        city = address.get('city', address.get('town', address.get('village', 'Unknown')))
        return city
    except GeopyError as e:
        return f"Error: {e}"

# Example usage
city = get_city(51.1, 0.1)
print(city)

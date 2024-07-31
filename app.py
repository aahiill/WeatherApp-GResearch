from flask import Flask, render_template
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError, GeocoderTimedOut
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Replace with your desired location coordinates
LATITUDE = 51.5  # Example: London
LONGITUDE = 0.12


def get_city(lat, long):
    try:
        geoLoc = Nominatim(user_agent="GetLoc")
        locname = geoLoc.reverse((lat, long), addressdetails=True)
        
        if locname is None:
            logging.debug(f"No location found for coordinates ({lat}, {long})")
            return 'N/A'
        
        address = locname.raw.get('address', {})
        city = address.get('city', address.get('town', address.get('village', 'Unknown')))
        logging.debug(f"Found city: {city}")
        return city
    except GeocoderTimedOut:
        logging.error("Geocoding service timed out")
        return "Geocoding service timed out"
    except GeopyError as e:
        logging.error(f"GeopyError: {e}")
        return f"Error: {e}"


@app.route('/')
def home():
    return render_template('forecast.html')


@app.route('/osm')
def osm():
    return render_template('osm.html')


if __name__ == '__main__':
    app.run(debug=True)

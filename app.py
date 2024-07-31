from flask import Flask, render_template, make_response
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
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
    # Setting up retries
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # OpenMeteo API endpoint
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&daily=temperature_2m_max,temperature_2m_min&timezone=Europe/Berlin"

    try:
        # Fetch weather data
        response = session.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        # Extract relevant information
        forecast = data['daily']
        dates = forecast['time']
        temp_max = forecast['temperature_2m_max']
        temp_min = forecast['temperature_2m_min']

        # Prepare data for rendering
        weekly_forecast = zip(dates, temp_max, temp_min)
        city = get_city(LATITUDE, LONGITUDE)
        logging.debug(f"City for coordinates ({LATITUDE}, {LONGITUDE}): {city}")

        # Create response
        response = make_response(render_template('forecast.html', weekly_forecast=weekly_forecast, city=city))
        
        # Add no-cache headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)

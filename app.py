from flask import Flask, render_template, request, make_response
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry #fixed import error
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import logging
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_city(lat, long):
    try:
        geoLoc = Nominatim(user_agent="GetLoc")
        locname = geoLoc.reverse((lat, long), addressdetails=True, language="en")
        address = locname.raw['address']
        
        city = address.get('city', address.get('town', address.get('village', 'Unknown')))
        country = address.get('country', 'Unknown')

        return f"{city}, {country}"
    except GeopyError as e:
        return f"Error: {e}"

def get_coords(city_name):
    """Retrieve latitude and longitude from city name."""
    try:
        geoLoc = Nominatim(user_agent="GetLoc")
        location = geoLoc.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeopyError as e:
        logging.error(f"GeopyError: {e}")
        return None, None

def get_today_date():
    today = datetime.now()
    return today.strftime('%Y-%m-%d')

def get_end_date(days):
    end_date = datetime.now() + timedelta(days=days)
    return end_date.strftime('%Y-%m-%d')

@app.route('/', methods=['GET'])
def home():
    """Handle the home route and display weather forecast."""
    # Get location from query parameter
    location = request.args.get('location', '')
    
    # Default coordinates if no location is provided
    latitude, longitude = 51.5, 0.12  # Default to London
    
    if location:
        latitude, longitude = get_coords(location)
        if latitude is None or longitude is None:
            latitude, longitude = 51.5, 0.12  # Fallback to default coordinates
            location = 'Location not found'

    # Setting up retries
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # OpenMeteo API endpoint
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
        f"&start_date={get_today_date()}"
        f"&end_date={get_end_date(7)}"
    )

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
        city = get_city(latitude, longitude)
        logging.debug(f"City and country for coordinates ({latitude}, {longitude}): {city}")

        # Create response
        response = make_response(render_template('forecast.html', weekly_forecast=weekly_forecast, city=city, location=location))
        
        # Add no-cache headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        return f"Error: {e}"

@app.route('/osm')
def osm():
    return render_template('osm.html')

@app.route('/map')
def map():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, make_response, jsonify
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
    location = request.args.get('location', '')
    latitude, longitude = 51.5, 0.12

    if location:
        latitude, longitude = get_coords(location)
        if latitude is None or longitude is None:
            latitude, longitude = 51.5, 0.12
            location = 'Location not found'

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
        f"&start_date={get_today_date()}"
        f"&end_date={get_end_date(7)}"
    )

    try:
        response = session.get(url)
        response.raise_for_status()
        data = response.json()

        forecast = data['daily']
        dates = forecast['time']
        temp_max = forecast['temperature_2m_max']
        temp_min = forecast['temperature_2m_min']
        temp_precip = forecast['precipitation_sum']
        temp_windspd = forecast['windspeed_10m_max']

        weekly_forecast = zip(dates, temp_max, temp_min, temp_precip, temp_windspd)
        city = get_city(latitude, longitude)

        response = make_response(render_template('home.html', weekly_forecast=weekly_forecast, city=city, location=location))
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

@app.route('/osm_widget')
def osm_widget():
    return render_template('osm_widget.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/get_city_name', methods=['GET'])
def get_city_name():
    lat = request.args.get('latitude')
    lon = request.args.get('longitude')
    
    if lat and lon:
        try:
            latitude = float(lat)
            longitude = float(lon)
            city_name = get_city(latitude, longitude)
            return jsonify({'city': city_name})
        except ValueError:
            return jsonify({'error': 'Invalid coordinates'}), 400
    return jsonify({'error': 'Coordinates not provided'}), 400

@app.route('/getCoords', methods=['GET'])
def get_coords_endpoint():
    city_name = request.args.get('city_name')
    if city_name:
        latitude, longitude = get_coords(city_name)
        if latitude is not None and longitude is not None:
            return jsonify({'latitude': latitude, 'longitude': longitude})
        else:
            return jsonify({'latitude': '51.5', 'longitude': '0.12'}), 200
    return jsonify({'error': 'City name not provided'}), 400

@app.route('/getHourlyWeather', methods=['GET'])
def get_hourly_weather():
    lat = request.args.get('latitude')
    lon = request.args.get('longitude')
    date = request.args.get('date')

    if lat and lon and date:
        try:
            latitude = float(lat)
            longitude = float(lon)
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={latitude}&longitude={longitude}"
                f"&hourly=temperature_2m,windspeed_10m,weather_code"
                f"&start_date={date}&end_date={date}"
                f"&timezone=auto"
            )
            
            response = session.get(url)
            response.raise_for_status()  # This will raise an error for HTTP codes 4xx/5xx
            data = response.json()

            if 'hourly' in data and data['hourly']:
                return jsonify(data)
            else:
                return jsonify({'error': 'No hourly data available'}), 500

        except ValueError as e:
            return jsonify({'error': 'Invalid coordinates'}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({'error': 'Error fetching weather data'}), 500
    else:
        return jsonify({'error': 'Coordinates or date not provided'}), 400


if __name__ == '__main__':
    app.run(debug=True)

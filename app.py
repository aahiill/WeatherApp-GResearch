from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import logging

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


@app.route('/', methods=['GET'])
def homepage():
    return render_template('homepage.html')

@app.route('/map_page')
def map_page():
    return render_template('map_page.html')

@app.route('/osm_widget')
def osm_widget():
    return render_template('osm_widget.html')

@app.route('/chart_page')
def chart_page():
    return render_template('chart_page.html')

@app.route('/scripts/<path:filename>')
def scripts_server(filename):
    return send_from_directory('scripts', filename)


@app.route('/getHourlyWeather', methods=['GET'])
def getHourlyWeather():
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

from flask import Flask, render_template
import requests

app = Flask(__name__)

# Replace with your desired location coordinates
LATITUDE = 52.52  # Example: Berlin
LONGITUDE = 13.405


@app.route('/')


def home():
    # OpenMeteo API endpoint
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&daily=temperature_2m_max,temperature_2m_min&timezone=Europe/Berlin"

    # Fetch weather data
    response = requests.get(url)
    data = response.json()

    # Extract relevant information
    forecast = data['daily']
    dates = forecast['time']
    temp_max = forecast['temperature_2m_max']
    temp_min = forecast['temperature_2m_min']

    # Prepare data for rendering
    weekly_forecast = zip(dates, temp_max, temp_min)

    return render_template('forecast.html', weekly_forecast=weekly_forecast, LATITUDE=LATITUDE, LONGITUDE=LONGITUDE)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
app = Flask(__name__)
@app.route('/')

def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
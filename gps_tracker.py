import gps
import time
from threading import Thread
from flask import Flask, jsonify
import requests
from config import BACKEND_URL, PORT

app = Flask(__name__)

gps_data = {"latitude": None, "longitude": None}

def get_gps_data():
    session = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    while True:
        try:
            report = session.next()
            if report['class'] == 'TPV':
                latitude = getattr(report, 'lat', None)
                longitude = getattr(report, 'lon', None)
                if latitude and longitude:
                    gps_data["latitude"] = latitude
                    gps_data["longitude"] = longitude
                    post_gps_data(latitude, longitude)
            time.sleep(1)
        except StopIteration:
            break

def post_gps_data(latitude, longitude):
    data = {'latitude': latitude, 'longitude': longitude}
    try:
        response = requests.post(BACKEND_URL, json=data)
        response.raise_for_status()
        print(f"Posted: {data}")
    except requests.RequestException as e:
        print(f"Failed to post data: {e}")

@app.route('/location', methods=['GET'])
def location():
    return jsonify(gps_data)

if __name__ == "__main__":
    # Start the GPS data collection in a separate thread
    gps_thread = Thread(target=get_gps_data)
    gps_thread.start()
    
    # Start the Flask web server
    app.run(host='0.0.0.0', port=PORT)

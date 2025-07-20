import json
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

RADIO_STATIONS = {}

def load_radio_stations():
    global RADIO_STATIONS
    try:
        with open('radio_stations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert list of stations to a dictionary keyed by a unique identifier (e.g., name or a generated ID)
            # For simplicity, let's use the name as the key, but ensure names are unique or generate a hash.
            RADIO_STATIONS = {station['name']: station for station in data}
            print(f"Loaded {len(RADIO_STATIONS)} stations from radio_stations.json")
    except FileNotFoundError:
        print("radio_stations.json not found. Please run scraper.py first.")
        exit(1)
    except json.JSONDecodeError:
        print("Error decoding radio_stations.json. Please check file format.")
        exit(1)

# Load stations when the app starts
load_radio_stations()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('.', path)

@app.route('/radio_stations', methods=['GET'])
def get_radio_stations():
    return jsonify(RADIO_STATIONS)

@app.route('/play_station/<station_id>', methods=['GET'])
def play_station(station_id):
    import urllib.parse
    decoded_station_id = urllib.parse.unquote(station_id)
    station = RADIO_STATIONS.get(decoded_station_id)
    if station and station.get('playable'):
        return jsonify({"message": f"Now playing {station['name']}", "stream_url": station['stream']})
    elif station:
        return jsonify({"error": f"{station['name']} is not currently playable"}), 400
    else:
        return jsonify({"error": "Station not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
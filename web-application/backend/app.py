from flask import Flask, jsonify, request
from datetime import datetime
from pathlib import Path
from flask_cors import CORS


from services.lookup import (
    load_data,
    search_stations,
    get_all_lines,
    get_lines_for_station,
    station_by_name,
    get_path_lengths,
    get_info_options,
)

from services.model_client import model_client

app = Flask(__name__)
CORS(app)

data_path = Path(__file__).parent.parent.parent / "data" / "connections_v3.csv"
load_data(str(data_path))



def parse_iso(s):
    return datetime.fromisoformat(s)




def build_features(payload):
    src_name = payload["src_station"]
    dst_name = payload["dst_station"]
    line = payload["line"]

    if src_name not in station_by_name or dst_name not in station_by_name:
        raise ValueError("Unknown station")

    src_meta = station_by_name[src_name]
    dst_meta = station_by_name[dst_name]

    src_eva = src_meta["eva_nr"]
    dst_eva = dst_meta["eva_nr"]

    src_pl, dst_pl = get_path_lengths(line, src_eva, dst_eva)

    src_plan = parse_iso(payload["src_arrival_plan"])
    dst_plan = parse_iso(payload["dst_arrival_plan"])
    start_ts = parse_iso(payload["start_timestamp"])

    ## Modified this to be correct
    if src_plan < start_ts:
        raise ValueError("src_arrival_plan must be >= start_timestamp")

    if dst_plan < src_plan:
        raise ValueError("dst_arrival_plan must be >= src_arrival_plan")

    src_delay = float(payload["src_arrival_delay"])

    return {
        "start_timestamp": payload["start_timestamp"],
        "line": line,
        "info": payload.get("info", ""),
        "src_station": src_name,
        "src_eva_nr": src_eva,
        "src_category": src_meta["category"],
        "src_path_length": src_pl,
        "src_arrival_plan": payload["src_arrival_plan"],
        "src_arrival_delay": src_delay,
        "dst_station": dst_name,
        "dst_eva_nr": dst_eva,
        "dst_category": dst_meta["category"],
        "dst_path_length": dst_pl,
        "dst_arrival_plan": payload["dst_arrival_plan"],
    }


# Flask routes

@app.route("/stations")
def stations():
    name = request.args.get("name", "")
    return jsonify(search_stations(name))


@app.route("/lines")
def lines():
    eva_nr = request.args.get("eva_nr")
    if eva_nr:
        return jsonify(get_lines_for_station(eva_nr))
    return jsonify(get_all_lines())


@app.route("/info-options")
def info_options():
    return jsonify(get_info_options())


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json()

    required = [
        "start_timestamp",
        "src_station",
        "dst_station",
        "line",
        "src_arrival_plan",
        "src_arrival_delay",
        "dst_arrival_plan",
    ]
    missing = [k for k in required if k not in payload]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        features = build_features(payload)
        result = model_client.predict(features)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
    
@app.route("/")
def index():
    return "DB delay backend is running.", 200


if __name__ == "__main__":
    # Changed to false to remove double-loading
    app.run(port=5530, debug=False)
# Backend API Documentation

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- `connections_v3.csv` file in the `../../data/` directory (relative to backend folder)

### Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python app.py
```

The server will start on `http://localhost:5530`

### Requirements

All required packages are listed in `requirements.txt`:
- `flask>=2.0.0` - Web framework
- `pandas>=1.3.0` - Data processing
- `python-Levenshtein>=0.12.0` - Fuzzy string matching

---

## Base URL

Base URL: `http://localhost:5530`

---

## Endpoints

### `GET /`
Health check endpoint.

**Response:**
```
DB delay backend is running.
```

---

### `GET /stations`
Search for train stations using fuzzy matching.

**Query Parameters:**
- `name` (optional): Search term for station name. If empty, returns all stations.

**Example Requests:**
```
GET /stations
GET /stations?name=Berlin%20Hbf
```

**Response:**
```json
[
  {
    "category": 1,
    "eva": 8011160,
    "name": "Berlin Hbf"
  }
]
```

---

### `GET /lines`
Get all available train lines or lines for a specific station.

**Query Parameters:**
- `eva_nr` (optional): Station EVA number. If provided, returns only lines serving this station.

**Example Requests:**
```
GET /lines
GET /lines?eva_nr=8011160
```

**Response:**
```json
[
  "FLX30",
  "RB23",
  "RB30",
  "RB56",
  "RE1",
  "RE2",
  "RE30",
  "RE35",
  "RE56",
  "RE7",
  "RE8",
  "S1",
  "S2",
  "S7",
  "S8"
]
```

---

### `GET /info-options`
Get all available info options.

**Example Request:**
```
GET /info-options
```

**Response:**
```json
[
  "Bauarbeiten",
  "Bauarbeiten. (Quelle: zuginfo.nrw)",
  "Gro\u00dfst\u00f6rung",
  "Information",
  "Information. (Quelle: zuginfo.nrw)",
  "St\u00f6rung",
  "St\u00f6rung. (Quelle: zuginfo.nrw)"
]
```

---

### `POST /predict`
Predict delay at destination station.

**Request Body:**
```json
{
    "start_timestamp": "2024-01-15T08:05:00",
    "src_station": "Aachen Hbf",
    "dst_station": "Köln Hbf",
    "line": "RE1",
    "src_arrival_plan": "2024-01-15T08:00:00",
    "src_arrival_delay": 3,
    "dst_arrival_plan": "2024-01-15T08:45:00",
    "info": "Signalstörung"
}
```

**Required Fields:**
- `start_timestamp` (ISO 8601): Trip start timestamp
- `src_station` (string): Source station name (exact match required)
- `dst_station` (string): Destination station name (exact match required)
- `line` (string): Train line name
- `src_arrival_plan` (ISO 8601): Planned arrival time at source
- `src_arrival_delay` (number): Current delay at source in minutes
- `dst_arrival_plan` (ISO 8601): Planned arrival time at destination

**Optional Fields:**
- `info` (string): Info status

**Response (200 OK):**
```json
{
  "dst_arrival_delay": 6.0,
  "dst_arrival_delay_over_10_minutes_prob": 0.3,
  "dst_arrival_delay_over_15_minutes_prob": 0.05,
  "dst_arrival_delay_over_20_minutes_prob": 0,
  "dst_arrival_delay_over_25_minutes_prob": 0,
  "dst_arrival_delay_over_30_minutes_prob": 0,
  "dst_arrival_delay_over_5_minutes_prob": 0.55,
  "dst_arrival_delay_over_6_minutes_prob": 0.5,
  "model_version": "placeholder_v1"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Missing fields: start_timestamp, src_station"
}
```

**Validation Rules:**
- `src_arrival_plan` must be <= `start_timestamp`
- `dst_arrival_plan` must be >= `src_arrival_plan`
- Both stations must exist in the database
- Both stations must be on the specified line
- Station names must match exactly (use `/stations` endpoint to get correct names)


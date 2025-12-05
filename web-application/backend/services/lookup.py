import pandas as pd
import Levenshtein

stations = []
stations_by_name = {}
stations_by_eva = {}
line_to_stations = {}
info_options = []

station_by_name = stations_by_name


def load_data(csv_path: str = "data/connections_v3.csv"):
    global stations, stations_by_name, stations_by_eva, line_to_stations, info_options

    print(f"Loading lookup data from {csv_path}...")
    print("[0%] Reading CSV file...", end="\r", flush=True)
    
    df = pd.read_csv(csv_path)
    print("[20%] CSV file loaded. Processing stations...", end="\r", flush=True)

    #all stations src + dst
    station_cols = ["src_station", "src_eva_nr", "src_category"]

    dst_as_src = df[["dst_station", "dst_eva_nr", "dst_category"]].rename(
        columns={
            "dst_station": "src_station",

            "dst_eva_nr": "src_eva_nr",
            "dst_category": "src_category",
        }
    )

    all_stations_df = (
        pd.concat([df[station_cols], dst_as_src[station_cols]], ignore_index=True)
        .drop_duplicates()
    )

    stations.clear()
    stations_by_name.clear()
    stations_by_eva.clear()

    total_stations = len(all_stations_df)
    for idx, (_, row) in enumerate(all_stations_df.iterrows()):
        name = row["src_station"]
        eva = int(row["src_eva_nr"])
        cat = int(row["src_category"])

        entry = {"name": name, "eva": eva, "category": cat}
        stations.append(entry)
        stations_by_name[name] = {"eva_nr": eva, "category": cat}
        stations_by_eva[eva] = {"name": name, "category": cat}
        
        if (idx + 1) % 100 == 0 or idx == total_stations - 1:
            progress = 20 + int((idx + 1) / total_stations * 40)
            print(f"  [{progress:3d}%] Processing stations ({idx + 1}/{total_stations})...", end="\r", flush=True)

    print("[60%] Stations processed. Processing lines...", end="\r", flush=True)

    # line + path lengths
    src_df = df[["line", "src_eva_nr", "src_path_length"]].rename(
        columns={"src_eva_nr": "eva_nr", "src_path_length": "path_length"}
    )
    dst_df = df[["line", "dst_eva_nr", "dst_path_length"]].rename(
        columns={"dst_eva_nr": "eva_nr", "dst_path_length": "path_length"}
    )

    line_station_df = (
        pd.concat([src_df, dst_df], ignore_index=True)
        .drop_duplicates()
    )

    line_to_stations.clear()
    lines = list(line_station_df.groupby("line"))
    total_lines = len(lines)
    for idx, (line, sub) in enumerate(lines):
        station_list = [
            {"eva_nr": int(r["eva_nr"]), "path_length": float(r["path_length"])}
            for _, r in sub.iterrows()
        ]
        station_list.sort(key=lambda x: x["path_length"])
        line_to_stations[line] = station_list
        
        if (idx + 1) % 10 == 0 or idx == total_lines - 1:
            progress = 60 + int((idx + 1) / total_lines * 30)
            print(f"  [{progress:3d}%] Processing lines ({idx + 1}/{total_lines})...", end="\r", flush=True)

    print("[90%] Lines processed. Loading info options...", end="\r", flush=True)

    #info options
    info_options.clear()
    if "info" in df.columns:
        info_options.extend(sorted(df["info"].dropna().unique()))
    else:
        print("Warning: 'info' column not found in CSV.")
    
    print("[100%] Data loading complete!")





def search_stations(name_substring: str, limit: int = 100):
    q = name_substring.lower()
    
    if not q:
        results = sorted(stations, key=lambda x: x["name"])
        return results[:limit]

    scored = []
    for s in stations:
        dist = Levenshtein.distance(q, s["name"].lower())
        scored.append((dist, s))

    scored.sort(key=lambda x: x[0]) 
    best = [s for dist, s in scored if dist <= 3] 

    return best[:limit]




def search_stations_by_name(name_substring: str, limit: int = 100):
    return search_stations(name_substring, limit)




def get_all_lines():
    return sorted(line_to_stations.keys())




def get_lines_for_station(eva_nr: int):
    eva_nr = int(eva_nr)
    lines = []
    for line, st in line_to_stations.items():
        if any(s["eva_nr"] == eva_nr for s in st):
            lines.append(line)
    return sorted(lines)



def get_path_lengths(line: str, src_eva_nr: int, dst_eva_nr: int):
    if line not in line_to_stations:
        raise ValueError(f"Unknown line: {line}")

    mapping = {s["eva_nr"]: s["path_length"] for s in line_to_stations[line]}

    if src_eva_nr not in mapping or dst_eva_nr not in mapping:
        raise ValueError("Source or destination station not on this line")

    src_pl = mapping[src_eva_nr]
    dst_pl = mapping[dst_eva_nr]

    if src_pl >= dst_pl:
        raise ValueError("src_path_length must be < dst_path_length")

    return src_pl, dst_pl



def get_info_options():
    return info_options

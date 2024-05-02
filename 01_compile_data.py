import csv
import json
import os
import glob

"""
Determines which years' data to load
"""
os.chdir(".")


def open_csv_file(filename):
    with open(filename, "r") as infile:
        data = csv.DictReader(infile)
        return list(data)


def open_json_file(filename):
    with open(filename, "r", encoding="utf-8") as infile:
        data = json.loads(infile.read())
        return data


def write_file(filename, data):
    with open(filename, "w") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")


YEARS = [2023, 2024]
MONTHS = {2023: [], 2024: ["02", "03"]}
BUS_SETS = True
FERRY_SETS = True
IGNORE_NONREV = True
SUBWAY_SETS = ["HR", "LR"]
CURRENT_DATE = "04-14-2024"
FERRY_STATION_NAMES = {
    "Lynn": "Boat-Blossom", # BOS - Lynn
    "Long Wharf S": "Boat-Long-South", # BOS - Charlestown (1) 
    "Rowes Wharf": "Boat-Rowes", # BOS - Hingham (direct) (2) 
    "Hingham": "Boat-Hingham", # BOS - Hingham/Hull/Georges Island/Logan or BOS - Hingham (direct)
    "Winthrop": "Boat-Winthrop", # BOS - Winthrop - Quincy - Logan - Seaport
    "Quincy": "Boat-Quincy", # BOS - Quincy - Winthrop - Logan - Seaport
    "Hull": "Boat-Hull", # BOS - Hingham/Hull/Georges Island/Logan
    "Logan": "Boat-Logan", # ...
    "Seaport": "Boat-Fan", # BOS - Seaport - ...
    "Lewis": "Boat-Lewis", # BOS - East Boston
    "Aquarium": "Boat-Aquarium", # BOS - Quincy - ... (3) 
    "Long Wharf N": "Boat-Long", # BOS - Hingham/Hull/Georges Island/Logan ... (4)
    "Georges": "Boat-George", # BOS - Georges Island / Hull / Hingham
    "Navy Yard": "Boat-Charlestown", # BOS - Charlestown
    "Boston": "Boat-Long", # BOS - Lynn (5)
    "Rowes": "Boat-Rowes"
}
ALL_MONTHS = False

if ALL_MONTHS:
    for year in YEARS:
        MONTHS[year] = []
        current_date_list = CURRENT_DATE.split("-")
        for month in range(12):
            if year * 12 + month > int(current_date_list[2]) * 12 + int(
                current_date_list[0]
            ):
                to_append = str(month)
                if len(to_append) == 1:
                    to_append = "0" + to_append
                MONTHS[year].append(to_append)

all_stops = open_json_file("stops.json")

stops_reformatted = {
    stop["id"]: (
        stop["attributes"]["name"],
        stop["attributes"]["latitude"],
        stop["attributes"]["longitude"],
    )
    for stop in all_stops["data"]
}

"""
full_data_set will be a dictionary with keys as follows:
- HR
- LR
- Bus
for each, we have a key for year, key for month, key for day, and list
"""
events = {}
trips = {}
important_stations = {}


def add_to_list(arr, obj):
    if obj not in arr:
        arr.append(obj)


for subway_set in SUBWAY_SETS:
    for year in YEARS:
        for month in MONTHS[year]:
            month_data = open_csv_file(
                f"subway_data/{year}_{subway_set}/{year}-{month}_{subway_set}Events.csv"
            )
            for item in month_data:
                line = item["route_id"]
                day = int(item["service_date"].split("-")[2])
                if (
                    IGNORE_NONREV
                    and len(item["trip_id"]) >= 6
                    and item["trip_id"][:6] == "NONREV"
                ):
                    continue
                reformatted_item = {
                    "year": year,
                    "month": int(month),
                    "day": day,
                    "time": int(item["event_time_sec"]),
                    "stop": item["stop_id"],
                    "direction": 1 if item['direction_id'] in ['1', 'Outbound'] else 0,
                    "type": item["event_type"],
                    "date": item["service_date"],
                    "route": item["route_id"],
                    "trip": item["trip_id"],
                }
                try:
                    reformatted_item["stop_name"] = stops_reformatted[
                        str(reformatted_item["stop"])
                    ][0]
                    date_list = events.get(reformatted_item["date"], {})
                    station_list = date_list.get(reformatted_item["stop_name"], {})
                    direction_list = station_list.get(reformatted_item["direction"], [])
                    direction_list.append(reformatted_item)
                    station_list[reformatted_item["direction"]] = direction_list
                    date_list[reformatted_item["stop_name"]] = station_list
                    events[reformatted_item["date"]] = date_list
                    trips[reformatted_item["date"]] = trips.get(
                        reformatted_item["date"], {}
                    )
                    trips[reformatted_item["date"]][reformatted_item["trip"]] = trips[
                        reformatted_item["date"]
                    ].get(reformatted_item["trip"], [])
                    trips[reformatted_item["date"]][reformatted_item["trip"]].append(
                        reformatted_item
                    )
                    important_stations[reformatted_item["stop_name"]] = (
                        important_stations.get(
                            reformatted_item["stop_name"], {"ids": {}, "routes": []}
                        )
                    )
                    important_stations[reformatted_item["stop_name"]]["ids"][
                        reformatted_item["stop"]
                    ] = important_stations[reformatted_item["stop_name"]]["ids"].get(
                        reformatted_item["stop"], []
                    )
                    add_to_list(
                        important_stations[reformatted_item["stop_name"]]["ids"][
                            reformatted_item["stop"]
                        ],
                        reformatted_item["route"],
                    )
                    add_to_list(
                        important_stations[reformatted_item["stop_name"]]["routes"],
                        reformatted_item["route"],
                    )
                    important_stations[reformatted_item["stop_name"]]['longitude'] = stops_reformatted[reformatted_item['stop']][2]
                    important_stations[reformatted_item["stop_name"]]['latitude'] = stops_reformatted[reformatted_item['stop']][1]
                except:
                    print(reformatted_item["stop"])

if BUS_SETS:
    for year in YEARS:
        for month in MONTHS[year]:
            month_data = open_csv_file(
                f"bus_data/{year}/MBTA-Bus-Arrival-Departure-Times_{year}-{month}.csv"
            )
            for item in month_data:
                if not item["actual"]:
                    continue
                line = item["route_id"]
                day = int(item["service_date"].split("-")[2])
                reformatted_item = {
                    "year": year,
                    "month": int(month),
                    "day": day,
                    "stop": item["stop_id"],
                    "direction": 1 if item['direction_id'] in ['1', 'Outbound'] else 0,
                    "type": "BUS",
                    "date": item["service_date"],
                    "route": item["route_id"],
                    "trip": item['half_trip_id']
                }
                try:
                    time = item["actual"]
                    reformatted_item["time"] = (
                        int(time.split(":")[1]) * 60
                        + int(time.split(":")[2][:2])
                        + int(time.split(":")[0][-2:]) * 3600
                        + (int(time.split("T")[0][-2:]) - 1) * 24 * 3600
                    )
                    reformatted_item["stop_name"] = stops_reformatted[
                        str(reformatted_item["stop"])
                    ][0]
                    date_list = events.get(reformatted_item["date"], {})
                    station_list = date_list.get(reformatted_item["stop_name"], {})
                    direction_list = station_list.get(reformatted_item["direction"], [])
                    direction_list.append(reformatted_item)
                    station_list[reformatted_item["direction"]] = direction_list
                    date_list[reformatted_item["stop_name"]] = station_list
                    events[reformatted_item["date"]] = date_list
                    trips[reformatted_item["date"]] = trips.get(
                        reformatted_item["date"], {}
                    )
                    trips[reformatted_item["date"]][reformatted_item["trip"]] = trips[
                        reformatted_item["date"]
                    ].get(reformatted_item["trip"], [])
                    trips[reformatted_item["date"]][reformatted_item["trip"]].append(
                        reformatted_item
                    )
                    important_stations[reformatted_item["stop_name"]] = (
                        important_stations.get(
                            reformatted_item["stop_name"], {"ids": {}, "routes": []}
                        )
                    )
                    important_stations[reformatted_item["stop_name"]]["ids"][
                        reformatted_item["stop"]
                    ] = important_stations[reformatted_item["stop_name"]]["ids"].get(
                        reformatted_item["stop"], []
                    )
                    add_to_list(
                        important_stations[reformatted_item["stop_name"]]["ids"][
                            reformatted_item["stop"]
                        ],
                        reformatted_item["route"],
                    )
                    add_to_list(
                        important_stations[reformatted_item["stop_name"]]["routes"],
                        reformatted_item["route"],
                    )
                    important_stations[reformatted_item["stop_name"]]['longitude'] = stops_reformatted[reformatted_item['stop']][2]
                    important_stations[reformatted_item["stop_name"]]['latitude'] = stops_reformatted[reformatted_item['stop']][1]
                except:
                    pass

if FERRY_SETS:
    month_data = open_csv_file(
        f"ferry_data/MBTA_Ferry_Trips.csv"
    )
    for item in month_data:
        if not item["actual_departure"] or not item["actual_arrival"]:
            continue
        line = item["route_id"]
        date = item["ï»¿service_date"].split(' ')[0].replace('/', '-')
        month = date.split('-')[1]
        year = int(date.split('-')[0])
        day = int(date.split('-')[2])
        reformatted_item = {
            "year": int(year),
            "month": int(month),
            "day": day,
            "direction": 1 if item['travel_direction'] in ['1', 'Outbound', 'From Boston'] else 0,
            "date": date,
            "route": item["route_name"],
            "trip": item['trip_id']
        }
        if not (month in MONTHS.get(year, []) and year in YEARS):
            continue
        reformatted_item_1 = reformatted_item.copy()
        try:
            reformatted_item["stop"] = FERRY_STATION_NAMES[item["departure_terminal"]]
            reformatted_item['stop_name'] = stops_reformatted[reformatted_item["stop"]]
            reformatted_item_1["stop"] = FERRY_STATION_NAMES[item["arrival_terminal"]]
            reformatted_item_1['stop_name'] = stops_reformatted[reformatted_item_1["stop"]]
            time = item["actual_departure"].split(' ')[1]
            reformatted_item['type'] = 'DEP'
            reformatted_item["time"] = (
                int(time.split(":")[1]) * 60
                + int(time.split(":")[0]) * 3600
            )
            time_1 = item["actual_arrival"].split(' ')[1]
            reformatted_item_1['type'] = 'ARR'
            reformatted_item_1["time"] = (
                int(time_1.split(":")[1]) * 60
                + int(time_1.split(":")[0]) * 3600
            )
            for reformatted_item in (reformatted_item, reformatted_item_1):
                reformatted_item["stop_name"] = stops_reformatted[
                    str(reformatted_item["stop"])
                ][0]
                date_list = events.get(reformatted_item["date"], {})
                station_list = date_list.get(reformatted_item["stop_name"], {})
                direction_list = station_list.get(reformatted_item["direction"], [])
                direction_list.append(reformatted_item)
                station_list[reformatted_item["direction"]] = direction_list
                date_list[reformatted_item["stop_name"]] = station_list
                events[reformatted_item["date"]] = date_list
                trips[reformatted_item["date"]] = trips.get(
                    reformatted_item["date"], {}
                )
                trips[reformatted_item["date"]][reformatted_item["trip"]] = trips[
                    reformatted_item["date"]
                ].get(reformatted_item["trip"], [])
                trips[reformatted_item["date"]][reformatted_item["trip"]].append(
                    reformatted_item
                )
                important_stations[reformatted_item["stop_name"]] = (
                    important_stations.get(
                        reformatted_item["stop_name"], {"ids": {}, "routes": []}
                    )
                )
                important_stations[reformatted_item["stop_name"]]["ids"][
                    reformatted_item["stop"]
                ] = important_stations[reformatted_item["stop_name"]]["ids"].get(
                    reformatted_item["stop"], []
                )
                add_to_list(
                    important_stations[reformatted_item["stop_name"]]["ids"][
                        reformatted_item["stop"]
                    ],
                    reformatted_item["route"],
                )
                add_to_list(
                    important_stations[reformatted_item["stop_name"]]["routes"],
                    reformatted_item["route"],
                )
                important_stations[reformatted_item["stop_name"]]['longitude'] = stops_reformatted[reformatted_item['stop']][2]
                important_stations[reformatted_item["stop_name"]]['latitude'] = stops_reformatted[reformatted_item['stop']][1]

        except:
            print(item["actual_departure"])


for date in events:
    for station in events[date]:
        for line in events[date][station]:
            try:
                events[date][station][line] = sorted(events[date][station][line], key=lambda x: int(x['time']))
            except:
                pass
    write_file(f"compiled_data/events/{date}-events.json", events[date])
for date, trips_in_day in trips.items():
    for trip_id, trip in trips_in_day.items():
        trips_in_day[trip_id] = sorted(trip, key=lambda x: x["time"])
    write_file(f"compiled_data/trips/{date}-trips.json", trips[date])
write_file(f"compiled_data/reformatted-stops.json", stops_reformatted)
write_file(f"compiled_data/important-stations.json", important_stations)

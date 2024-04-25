import json
import os
import math

dates = []
potential_trips = [[26500, (42.305045,-70.9172807), (42.3602635,-71.0881715)]]
os.chdir(".")
EARTH_RADIUS = 6.371 * 10**6
WALKING_SPEED = 1.75
ADDITIONAL_DISTANCE_FACTOR = 1.20
MAX_WAIT_TIME = 180 * 60

"""
trips: 
[
    [
        start time, start location, end location
    ],
    ...
]
"""


def str_form(year, month, day):
    str_month = str(month)
    str_day = str(day)
    if len(str_month) == 1:
        str_month = "0" + str_month
    if len(str_day) == 1:
        str_day = "0" + str_day
    return f"{year}-{str_month}-{str_day}"


for i in range(1, 32):
    dates.append(str_form(2023, 7, i))

results = []

"""
Results: 
[
    [start time, (start location), (end location), 
        [
            date, time of arrival, 
            [(ID, starting location/coords, ending location/coords)]
        ],
        ...
    ],
    [...]
    ...
]
"""


def open_json_file(filename):
    with open(filename, "r", encoding="utf-8") as infile:
        data = json.loads(infile.read())
        return data


def write_file(filename, data):
    with open(filename, "w") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")


STATIONS = open_json_file("compiled_data/important-stations.json")
STATION_COORDS = open_json_file("compiled_data/reformatted-stops.json")
station_times_template = {
    name: {
        "out-routes": [
            *[(route, "0") for route in station["routes"]],
            *[(route, "1") for route in station["routes"]],
            "walk",
        ],
        "earliest-time": 10**10,
        "location": (station["latitude"], station["longitude"]),
        "trip-taken": None,
    }
    for name, station in STATIONS.items()
}


def estimate_walking_time(lat1, long1, lat2, long2):
    """Note that this is not really the 'correct' walk time is'"""
    dist1 = (long1 - long2) * EARTH_RADIUS * math.pi / 180
    dist2 = (lat1 - lat2) * EARTH_RADIUS * math.pi / 180
    est_dist = ADDITIONAL_DISTANCE_FACTOR * (dist1**2 + dist2**2) ** 0.5
    return est_dist / WALKING_SPEED


def update_times_stations_walking(
    start_location, start_time, station_template, end_location, initializing=False, start_station = False):
    for name, station in station_template.items():
        try:
            est_time = start_time + estimate_walking_time(
                *start_location, *station["location"]
            ) + 30
            if initializing or est_time < station["earliest-time"]:
                station["earliest-time"] = est_time
                if initializing and not start_station:
                    station["trip-taken"] = [("walk", start_location, est_time, name)]
                else:
                    station["trip-taken"] = station_template[start_station]["trip-taken"].copy()
                    station["trip-taken"].append(("walk", start_station, est_time, name))
        except:
            print('aaaaa')
    output = start_time + estimate_walking_time(*start_location, *end_location) + 30
    return output


def update_times_stations_transit(start_station_name, current_trip, station_template, first_station_arrival):
    try:
        index_of_station = -1
        station_found = False
        while station_found is not True:
            index_of_station += 1
            if current_trip[index_of_station][
                "stop_name"
            ] == start_station_name and current_trip[index_of_station]["type"] in [
                "DEP",
                "PRD",
                "BUS",
            ] and current_trip[index_of_station]["time"] >= first_station_arrival:
                station_found = True
        for event in current_trip[index_of_station + 1 :]:
            if event["type"] in ["ARR", "BUS", "PRA"]:
                station_name = event["stop_name"]
                if station_template[station_name]["earliest-time"] > event["time"] + 30:
                    station_template[station_name]["earliest-time"] = event["time"] + 30
                    station_template[station_name]["trip-taken"] = station_template[start_station_name]["trip-taken"].copy()
                    station_template[station_name]["trip-taken"].append(((event["route"], event["trip"]), start_station_name, event["time"] + 30, station_name))
                else:
                    break
    except:
        pass


def solve_trip(
    end_location, current_fastest_time, station_template, events_today, trips_today, fastest_station = None, station_names=None
):
    if station_names is None:
        station_names = sorted(
            station_template.keys(), key=lambda x: station_template[x]["earliest-time"]
        )
    first_station_to_check = station_names.pop(0)
    # print(first_station_to_check)
    arrives_at_first_station = station_template[first_station_to_check]['earliest-time']
    if arrives_at_first_station is None:
        return current_fastest_time
    if arrives_at_first_station >= current_fastest_time:
        return None
    for i, route in enumerate(station_template[first_station_to_check].get('out-routes', ['walk'])):
            # print(route)
            if route == "walk":
                fastest_time_from_station = update_times_stations_walking(station_template[first_station_to_check]['location'], station_template[first_station_to_check]['earliest-time'], station_template, end_location, False, first_station_to_check)
                if fastest_time_from_station < current_fastest_time:
                    current_fastest_time = fastest_time_from_station
                    #print(first_station_to_check)
                    fastest_station = first_station_to_check
            else:
                line, dir = route[0], route[1]
                if first_station_to_check in events_today and dir in events_today[first_station_to_check]:
                    for event in events_today[first_station_to_check][dir]:
                        if int(event['time']) >= current_fastest_time:
                            # print('okay')
                            pass
                        elif int(event['time']) >= arrives_at_first_station and event['type'] in ['DEP', 'PRD', 'BUS'] and event['route'] == line:
                            # print(route)
                            update_times_stations_transit(first_station_to_check, trips_today[event['trip']], station_template, arrives_at_first_station)
                            break
    return (current_fastest_time, fastest_station)

print(estimate_walking_time(42.310349, -71.107332, 42.317062, -71.104248) + estimate_walking_time(42.317062, -71.104248, 42.323074, -71.099546) - estimate_walking_time(42.310349, -71.107332, 42.323074, -71.099546))

for date in dates:
    for potential_trip in potential_trips:
        events_today = open_json_file(f"compiled_data/events/{date}-events.json")
        trips_today = open_json_file(f"compiled_data/trips/{date}-trips.json")
        station_times = station_times_template.copy()

        (start_time, start_location, end_location) = potential_trip[:4]
        update_times_stations_walking(start_location, start_time, station_times, end_location, True)
        # print(list(station_times.items())[:10])

        current_fastest_time = estimate_walking_time(*start_location, *end_location) + start_time
        # print(current_fastest_time)
        last_output = (current_fastest_time, None)

        station_names = sorted(
            station_times.keys(), key=lambda x: station_times[x]["earliest-time"]
        )
        fastest_station = None

        while last_output is not None:
            last_output = solve_trip(end_location, current_fastest_time, station_times, events_today, trips_today, last_output[1], station_names)
            station_names = sorted(station_names, key = lambda x: station_times[x]['earliest-time'])
            if last_output is not None and last_output[0] <= current_fastest_time:
                current_fastest_time = last_output[0]
                fastest_station = last_output[1]
            # print(current_fastest_time)
        final_time = current_fastest_time - start_time
        print(f'{final_time // 3600} hours, {(final_time // 60) % 60} minutes, {((final_time // 1)) % 60} seconds')
        if fastest_station is not None:
            print(date)
            print([item for item in station_times[fastest_station]["trip-taken"]])
import json
import os
import math
# MIT Building 7: 42.3590587, -71.0934272
# Kendall - 42.3624332, -71.0853644
# Alewife - 42.3960896, -71.1424221
# Revere Beach - 42.4130136, -70.9894010
# Boston Common Statue - 42.3542693, -71.0655757
# Hingham - 42.2523060, -70.9195660
# Spicy Hunan Kitchen - 42.4804598, -71.1520056
# Waltham Square - 42.3751430, -71.2357254


dates = []

YEARS = [2023, 2024]
MONTHS = {2023: [], 2024: ["02", "03"]}
NUM_OF_DAYS = {
    "01": 31,
    "02": (28, 29),
    "03": 31,
    "04": 30,
    "05": 31,
    "06": 30,
    "07": 31,
    "08": 31,
    "09": 30,
    "10": 31,
    "11": 30,
    "12": 31
}

def prompt(text, type):
    output = input(text)
    try:
        return type(output)
    except:
        print(f'Invalid response. Please type a {type}.')
        return prompt(text, type)

hhmmss = prompt('Please enter the starting time in hh:mm:ss format (24-hour time): ', str)
start_time = 3600 * int(hhmmss[:2]) + 60 * int(hhmmss[3:5]) + 60 * int(hhmmss[6:])
start_lat = prompt('Please enter your starting location\'s latitude: ', float)
start_long = prompt('Please enter your starting location\'s longitude: ', float)
end_lat = prompt('Please enter your ending location\'s latitude: ', float)
end_long = prompt('Please enter your ending location\'s latitude: ', float)

potential_trips = [[start_time, (start_lat, start_long), (end_lat, end_long)]]
os.chdir(".")
EARTH_RADIUS = 6.371 * 10**6
WALKING_SPEED = prompt('Please enter your walking speed, in meters per second: ', float)
ADDITIONAL_DISTANCE_FACTOR = 1.20
MAX_WAIT_TIME = 180 * 60
all_times = []

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

def standard_time(secs):
    hrs = str(int(secs // 3600))
    mins = str(int((secs % 3600) // 60))
    secs = str(int((secs % 60) // 1))
    if len(hrs) < 2:
        hrs = '0' + hrs
    if len(mins) < 2:
        mins = '0' + mins
    if len(secs) < 2:
        secs = '0' + secs
    return f'{hrs}:{mins}:{secs}'

def leap_year(year):
    if year % 4 > 0:
        return False
    if year % 100 > 0:
        return True
    if year % 400 == 0:
        return True
    return False

for year in YEARS:
    for month in MONTHS[year]:
        num_days = NUM_OF_DAYS[month]
        if isinstance(num_days, tuple):
            num_days = num_days[int(leap_year(year))]
        for day in range(1, num_days + 1):
            dates.append(str_form(year, month, day))


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

def sort_and_trim(trips_taken):
    output = sorted(trips_taken, key = lambda x: (x[0], x[1]))
    return output[:min(len(output), 50)]



def sort_trim_and_cut_duplicates(trips_taken):
    output = sorted(trips_taken, key = lambda x: (x[0], x[1]))
    routes = [[leg[0] for leg in trip[2] if isinstance(leg[0], tuple)] for _, trip in enumerate(trips_taken)]
    unique_routes = []
    indices_to_eliminate = []
    for i, route in enumerate(routes):
        if route not in unique_routes:
            unique_routes.append(route)
        else:
            indices_to_eliminate.append(i)
    for index in indices_to_eliminate[::-1]:
        output.pop(index)
    return output[:min(len(output), 20)]


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
                    station["trip-taken"] = [[est_time, 1, [("walk", start_location, est_time, name)]]]
                else:
                    for i in range(min(5, len(station_template[start_station]["trip-taken"]))):
                        station['trip-taken'].append([*station_template[start_station]["trip-taken"][i][:2], station_template[start_station]["trip-taken"][i][2].copy()])
                        station['trip-taken'][-1][2].append(("walk", start_location, est_time - start_time + station['trip-taken'][-1][0], name))
                        station['trip-taken'][-1][1] += 1
                        station['trip-taken'][-1][0] = est_time - start_time + station['trip-taken'][-1][0]
                    station["trip-taken"] = sort_and_trim(station["trip-taken"])
        except:
            print(len(station_template[name]["trip-taken"]))
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
                    station = station_template[station_name]
                    station_template[station_name]["earliest-time"] = event["time"] + 30
                    for i in range(min(5, len(station_template[start_station_name]["trip-taken"]))):
                        station['trip-taken'].append([*station_template[start_station_name]["trip-taken"][i][:2], station_template[start_station_name]["trip-taken"][i][2].copy()])
                        station['trip-taken'][-1][2].append(((event["route"], event["direction"]), start_station_name, event["time"] + 30 + station['trip-taken'][-1][0] - first_station_arrival, station_name))
                        station['trip-taken'][-1][0] = event["time"] + 30 + station['trip-taken'][-1][0] - first_station_arrival
                    station['trip-taken'] = sort_trim_and_cut_duplicates(station['trip-taken'])
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
    try:
        first_station_to_check = station_names.pop(0)
    except:
        return None
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

for date in dates:
    for potential_trip in potential_trips:
        events_today = open_json_file(f"compiled_data/events/{date}-events.json")
        trips_today = open_json_file(f"compiled_data/trips/{date}-trips.json")
        station_times = {
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
        all_times.append((date, final_time, station_times[fastest_station]))
        print(f'Fastest time on {date}: {final_time // 3600} hours, {(final_time // 60) % 60} minutes, {((final_time // 1)) % 60} seconds')
        if fastest_station is not None:
            print(date, fastest_station)
            # print(station_times[fastest_station]["trip-taken"][0])
            # print([[standard_time(trip[0]), trip[1], [leg[0] for leg in trip[2] if isinstance(leg[0], tuple)]] for _, trip in enumerate(sort_trim_and_cut_duplicates(station_times[fastest_station]["trip-taken"]))])

def rnd(num, digits = 0):
    output = num * 10 ** digits
    output = round(output)
    return output / (10 ** digits)

def find_stats(all_times):
    sorted_list = sorted(all_times, key = lambda x: x[1])
    output = {
        'median': (0.5 * (sorted_list[len(sorted_list) // 2][1]) + 0.5 * (sorted_list[-(len(sorted_list) // 2)][1])),
        'mean': sum(x[1] for x in all_times) / len(all_times),
        'minimum': sorted_list[0][1],
        'maximum': sorted_list[-1][1],
    }
    output['standard_deviation'] = ((sum((x[1] - output['mean']) ** 2 for x in all_times)) / (len(all_times) - 1)) ** 0.5
    return output
all_times_dict = {item[0]: item for item in all_times}
write_file(f'trips/{start_time} - ({rnd(start_lat, 5)}, {rnd(start_long, 5)}) to ({rnd(end_lat, 5)}, {rnd(end_long, 5)}).json', all_times_dict)
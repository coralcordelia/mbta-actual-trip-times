import json
import os
import math

def prompt(text, type):
    output = input(text + '\n')
    try:
        return type(output)
    except:
        print(f'Invalid response. Please type a {type}.')
        prompt(text, type)

def open_json_file(filename):
    with open(filename, "r", encoding="utf-8") as infile:
        data = json.loads(infile.read())
        return data

filename = prompt('Enter in the filename and path of your trip: ', str)
trips_to_evaluate = open_json_file(filename)


def write_file(filename, data):
    with open(filename, "w") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

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

def find_fastest_routes(all_times):
    output = {}
    for trip in all_times:
        fastest_path = trip[2]['trip-taken'][0][2]
        just_text = tuple(leg[0][0] for leg in fastest_path if isinstance(leg[0], list))
        output[just_text] = output.get(just_text, 0) + 1
    return output

def find_all_routes(trips_on_a_day, fastest_time, limit = 50):
    route_sequences = [[event[0][0] for event in trip[2] if isinstance(event[0], list)] for trip in trips_on_a_day]
    output = ''
    num = 0
    for route in route_sequences[:min(len(route_sequences), limit)]:
        num += 1
        output += f'{num}.'
        for line in route:
            output += f' {line} -'
        output += '- ' + str(standard_time(fastest_time - trips_on_a_day[0][0] + trips_on_a_day[num - 1][0])) + '\n'
    return output




def format_fastest_routes(fastest_routes):
    sorted_list = sorted(list(fastest_routes.keys()), key = lambda x: fastest_routes[x], reverse = True)
    output = ''
    for route in sorted_list:
        route_string = ''
        for line in route:
            route_string += f'Take the {line}, then '
        if route_string == '':
            route_string = 'Walk to your final destination.'
        else:
            route_string = route_string[:-7] + '. '
        route_string += f'This route was fastest on {fastest_routes[route]} of the {len(trips_to_evaluate)} days.\n'
        output += route_string
    return output
        
def format_one_trip(trip, fastest_time):
    num = 0
    output = ''
    for event in trip[2]:
        num += 1
        if event[0] == 'walk':
            output += f'{num}. Walk to {event[3]}.\n'
        else:
            output += f'{num}. Take the {event[0][0]} to {event[3]}.\n'
    final_time = fastest_time
    output += f'{num+1}. Walk to your final destination. \nYou will take {final_time // 3600} hours, {(final_time // 60) % 60} minutes, {((final_time // 1)) % 60} seconds and arrive at {standard_time(trip[0])}'
    return output

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

def format_stats(stats):
    output = ''
    for name, num in stats.items():
        output += f'{name}: {standard_time(round(num))}\n'
    return output

next_request = None
while True:
    next_request = prompt('What would you like to do next? Type A to get trip statistics, and type B to get the trips from a specific day. Type N to leave.', str)
    if next_request == 'A':
        next_request = prompt('Type A if you want general time statistics, and type B if you want the most frequent fastest routes.', str)
        if next_request == 'A':
            print(format_stats(find_stats(trips_to_evaluate.values())))
        elif next_request == 'B':
            print(format_fastest_routes(find_fastest_routes(trips_to_evaluate.values())))
        else:
            print('Invalid request. Starting over.')
            continue
    elif next_request == 'B':
        next_request = prompt('Type the date you want to look at (yyyy-mm-dd): ', str)
        if next_request in trips_to_evaluate.keys():
            date = next_request
            next_request = prompt('Press A if you want the fastest route, and B if you want to see all the routes found.', str)
            if next_request == 'A':
                print(format_one_trip(trips_to_evaluate[date][2]['trip-taken'][0], trips_to_evaluate[date][1]))
            elif next_request == 'B':
                print(find_all_routes(trips_to_evaluate[date][2]['trip-taken'], trips_to_evaluate[date][1]))
            else:
                print('Invalid request. Starting over.')
                continue
        else:
            print('Date not found. Exiting and starting again.')
    elif next_request == 'N':
        print('Exiting...')
        break
    else:
        print('Invalid request. Starting over.')

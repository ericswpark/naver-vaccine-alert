import ast
import json
import os
import sys
import time
import requests
import pprint

from blessed import Terminal

# Global vars
run_count = 0       # DO NOT CHANGE
term = Terminal()   # DO NOT CHANGE
time_delay = 10     # Use values above 3 seconds


def main():
    global run_count, time_delay

    # Clear screen
    term.clear()

    with term.cbreak():
        val = ''
        while True:
            if run_count == 0:
                print("Starting in {} seconds...".format(time_delay))

            print_help()
            val = term.inkey(timeout=time_delay)

            if val.name == 'KEY_UP':
                adjust_time_delay(1)
            elif val.name == 'KEY_DOWN':
                adjust_time_delay(-1)
            elif val.lower() == 'q':
                break
            elif val.lower() == 'r' or not val:
                print()     # Skip to newline to get rid of prompt
                fetch_vaccine_info()
                run_count += 1


def print_help():
    print("Press q to quit, down/up arrow keys to adjust time delay, or r to refresh", end='')
    sys.stdout.flush()


def adjust_time_delay(adj):
    global time_delay

    time_delay += adj
    if adj > 0:
        print("\nIncreased time delay by {}, new time delay: {}".format(adj, time_delay))
    else:
        print("\nDecreased time delay by {}, new time delay: {}".format(-adj, time_delay))


def parse_local_response_data():
    with open('response.json', 'r') as file:
        raw = file.read()
        data = ast.literal_eval(raw)
    parse_vaccine_data(data)


def parse_vaccine_data(data):
    locations = data[0]['data']['rests']['businesses']['items']

    for location in locations:
        vaccine_count = location['vaccineQuantity']['totalQuantity']

        if vaccine_count > 0:
            pprint.pprint(location)
            play_alert(duration=1)
            play_message("FOUND FREE VACCINES")
        else:
            print("{} - run {} - {} has no vaccines...".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                               run_count, location['name']))


def fetch_vaccine_info():
    url = "https://api.place.naver.com/graphql"

    with open('request.json') as file:
        data = json.load(file)

    r = requests.post(url, json=data)

    if r.status_code == 200:
        # Save response to file
        with open('response.json', 'w') as file:
            file.write(json.dumps(r.json(), indent=4, sort_keys=True, ensure_ascii=False))
            file.flush()

        # Do things with the data
        parse_vaccine_data(r.json())
    else:
        print("There was a problem fetching from Naver's API.\n")


# Play alert
# Duration in seconds, frequency in Hz
def play_alert(duration=3, freq=2000):
    for i in range(0, 5):
        os.system('play -nq synth {} sine {}'.format(duration / 5, freq))
        time.sleep(0.2)


def play_message(message):
    os.system('say "{}"'.format(message))


if __name__ == '__main__':
    main()

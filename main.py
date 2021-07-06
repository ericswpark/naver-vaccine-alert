import ast
import json
import os
import sys
import time
import requests
import pprint
import configparser
import logging

from pushover import Client
from blessed import Terminal

# Global vars
run_count = 0
term = Terminal()

# Read from configuration
config = configparser.ConfigParser()

if not os.path.exists('config.ini'):
    print("The configuration file does not exist. Please refer to the README and create a configuration file.")
    exit(1)

config.read('config.ini')

time_delay = int(config['DEFAULT']['time-delay'])
pushover_notifications_enabled = (config['DEFAULT']['pushover-notifications'].lower() == "true")
local_notifications_enabled = (config['DEFAULT']['local-notifications'].lower() == "true")

if pushover_notifications_enabled:
    api_token = config['pushover']['api-token']
    user_key = config['pushover']['user-key']

    client = Client(user_key=user_key, api_token=api_token)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh = logging.FileHandler('log.txt')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)


def main():
    global run_count, time_delay

    # Clear screen
    term.clear()

    with term.cbreak():
        while True:
            if run_count == 0:
                logger.info("Starting in {} seconds...".format(time_delay))
                logger.info("Press q to quit, down/up arrow keys to adjust time delay, or r to refresh")

            val = term.inkey(timeout=time_delay)

            if val.name == 'KEY_UP':
                adjust_time_delay(1)
            elif val.name == 'KEY_DOWN':
                adjust_time_delay(-1)
            elif val.lower() == 'q':
                break
            elif val.lower() == 'r' or not val:
                fetch_vaccine_info()
                run_count += 1


def adjust_time_delay(adj):
    global time_delay

    time_delay += adj
    if adj > 0:
        logger.info("\nIncreased time delay by {}, new time delay: {}".format(adj, time_delay))
    else:
        logger.info("\nDecreased time delay by {}, new time delay: {}".format(-adj, time_delay))


def parse_local_response_data():
    with open('response.json', 'r') as file:
        raw = file.read()
        data = ast.literal_eval(raw)
    parse_vaccine_data(data)


def parse_vaccine_data(data):
    locations = data[0]['data']['rests']['businesses']['items']
    found_vaccines = False

    for location in locations:
        vaccine_count = location['vaccineQuantity']['totalQuantity']

        if vaccine_count > 0:
            print_log("Found vaccine, location data:")
            pprint.pprint(location)
            found_vaccines = True

            trigger_pushover_notification(location, vaccine_count)
            trigger_local_notification()

    if not found_vaccines:
        print_log("No vaccines found on this run.")


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def print_log(msg):
    logger.info("{} - run {}: {}".format(get_current_time(), run_count, msg))


def trigger_pushover_notification(location, vaccine_count):
    if pushover_notifications_enabled:
        # Check vaccine type
        vaccine_type = location['vaccineQuantity']['list'][0]['vaccineType']
        if vaccine_type == '화이자':
            client.send_message("Found Pfizer vaccines at {}!\nAddress: {}\nVaccine count: {}"
                                .format(location['name'], location['roadAddress'], vaccine_count), priority=1)
        else:
            client.send_message("Found vaccines at {}!\nAddress: {}\nVaccine count: {}\nVaccine type: {}"
                                .format(location['name'], location['roadAddress'], vaccine_count, vaccine_type))


def trigger_local_notification():
    if local_notifications_enabled:
        play_alert(duration=1)
        play_message("Found vaccines")


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
        try:
            parse_vaccine_data(r.json())
        except Exception as e:
            print_log("Warning: an error occurred while trying to parse the output.")
            logger.error(e)
    else:
        print_log("There was a problem fetching from Naver's API on this run.")


# Play alert
# Duration in seconds, frequency in Hz
def play_alert(duration=3, freq=2000):
    if sys.platform != "win32":
        for i in range(0, 5):
            os.system('play -nq synth {} sine {}'.format(duration / 5, freq))
            time.sleep(0.2)


def play_message(message):
    if sys.platform == "darwin":
        os.system('say "{}"'.format(message))


if __name__ == '__main__':
    main()

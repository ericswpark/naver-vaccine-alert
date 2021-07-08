#!/usr/bin/env python

import ast
import json
import os
import requests
import pprint
import configparser
import logging
import urllib.parse

from pushover import Client
from blessed import Terminal

# Global vars
run_count = 0
term = Terminal()

# Read from configuration
config = configparser.ConfigParser()

if not os.path.exists('config.ini'):
    logging.error("The configuration file does not exist. Please refer to the README and create a configuration file.")
    exit(1)

config.read('config.ini')

time_delay = int(config['DEFAULT']['time-delay'])
pushover_notifications_enabled = (config['DEFAULT']['pushover-notifications'].lower() == "true")

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

formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)


def main():
    global run_count, time_delay

    # Clear screen
    term.clear()

    # Set up cbreak
    ctx = None

    try:
        ctx = term.cbreak()
        ctx.__enter__()
        while True:
            if run_count == 0:
                logger.info("Starting in {} seconds...".format(time_delay))
                print_help()

            val = term.inkey(timeout=time_delay)

            if val.lower() == 'q':
                break
            elif val.lower() == 't':
                ctx.__exit__(None, None, None)
                set_time_delay()
                ctx = term.cbreak()
                ctx.__enter__()
            elif val.lower() == 'h':
                print_help()
            elif val.lower() == 'r' or not val:
                fetch_vaccine_info()
                run_count += 1
    finally:
        if ctx is not None:
            ctx.__exit__(None, None, None)


def print_help():
    logger.info("\tr - Refresh manually once")
    logger.info("\tt - Set new time delay")
    logger.info("\th - Show this help menu")
    logger.info("\tq - Quit")


def set_time_delay():
    global time_delay

    time_delay = int(input("Enter new time delay in seconds (integers only): "))

    logger.info("New time delay: {}".format(time_delay))


def parse_local_response_data():
    with open('response.json', 'r') as file:
        raw = file.read()
        data = ast.literal_eval(raw)
    parse_vaccine_data(data)


def parse_vaccine_data(data):
    locations = data[0]['data']['rests']['businesses']['items']
    found_vaccines = False

    for location in locations:
        try:
            vaccine_count = location['vaccineQuantity']['totalQuantity']
        except TypeError:
            # This location doesn't have any vaccines
            continue

        if vaccine_count > 0:
            print_log("Found vaccine, location data:")
            print_log(pprint.pformat(location))
            found_vaccines = True

            trigger_pushover_notification(location, vaccine_count)

    if not found_vaccines:
        print_log("No vaccines found.")


def print_log(msg):
    logger.info("Run {}: {}".format(run_count, msg))


def trigger_pushover_notification(location, vaccine_count):
    if pushover_notifications_enabled:
        # Check vaccine type
        vaccine_type = location['vaccineQuantity']['list'][0]['vaccineType']
        if vaccine_type == '화이자':
            client.send_message("Found Pfizer vaccines at {}!\nAddress: {}\nVaccine count: {}"
                                .format(location['name'], location['roadAddress'], vaccine_count), priority=1,
                                url=get_redirect_url(location['id']), url_title="Go to location page")
        else:
            client.send_message("Found vaccines at {}!\nAddress: {}\nVaccine count: {}\nVaccine type: {}"
                                .format(location['name'], location['roadAddress'], vaccine_count, vaccine_type),
                                url=get_redirect_url(location['id']), url_title="Go to location page")


def get_redirect_url(location_id):
    url = "https://m.place.naver.com/hospital/{}/home".format(location_id)
    return "naversearchapp://inappbrowser?url={}".format(urllib.parse.quote_plus(url))


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
            # Print trace
            import traceback
            traceback.print_exc()
    else:
        print_log("There was a problem fetching from Naver's API on this run.")


if __name__ == '__main__':
    main()

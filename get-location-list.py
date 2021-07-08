#!/usr/bin/env python

import json
import argparse

parser = argparse.ArgumentParser(description='Process response.json from main.py')
parser.add_argument('-f', '--find', help='Find hospital from list')

hospitals = []


def parse_response_data():
    with open('response.json', 'r') as file:
        data = json.load(file)

    locations = data[0]['data']['rests']['businesses']['items']

    for location in locations:
        location_name = location['name']
        try:
            vaccine_count = location['vaccineQuantity']['totalQuantity']
        except TypeError:
            # No vaccines in this location
            vaccine_count = 0
        hospitals.append({'name': location_name, 'count': vaccine_count})


def print_location_data():
    parse_response_data()
    for location in hospitals:
        print("{} - {} vaccines".format(location['name'], location['count']))


def find_location(name):
    parse_response_data()
    found_location = False
    for location in hospitals:
        if name in location['name']:
            print("Found location {}. Vaccine count: {}".format(location['name'], location['count']))
            found_location = True

    if not found_location:
        print("No location found.")


def main():
    args = parser.parse_args()
    if args.find:
        find_location(args.find)
    else:
        print_location_data()
        print("Total locations: {}".format(hospitals.count()))


if __name__ == "__main__":
    main()

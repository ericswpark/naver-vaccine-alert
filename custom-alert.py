#!/usr/bin/env python

import os
import configparser
import logging

from pushover import Client

# Read from configuration
config = configparser.ConfigParser()

if not os.path.exists('config.ini'):
    logging.error("The configuration file does not exist. Please refer to the README and create a configuration file.")
    exit(1)

config.read('config.ini')

api_token = config['pushover']['api-token']
user_key = config['pushover']['user-key']

client = Client(user_key=user_key, api_token=api_token)


def main():
    message = input("Enter message you want to send: ")
    url = input("Enter URL you want to send: ")
    client.send_message(message=message, url=url, priority=1)


if __name__ == '__main__':
    main()

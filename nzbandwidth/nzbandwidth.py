#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division
import requests
from time import sleep
import json
import math
import logging


def plexpy_get_activity(base_url, apikey):
    url = '{base_url}/api/v2'.format(base_url=base_url)
    params = dict(apikey=apikey,
                  cmd="get_activity"
                  )
    # TODO: Look at PlexPy's return data for errors and handle these accordingly
    try:
        response = requests.get(url, params=params).json()
        return response["response"]["data"]
    except KeyError:
        return None


def nzbget_set_rate(base_url, user, password, rate=0):

    # Build a JSON-RPC compatible object which tells nzb what to set the speed limit to
    data = dict(method="rate", params=rate, jsonrpc="2.0", id=0)
    headers = {'content-type': 'application/json'}
    url = "{base_url}/{user}:{passwd}/jsonrpc".format(base_url=base_url,
                                                      user=user,
                                                      passwd=password).encode('utf-8')

    # Send our request, data dict object must be run through json.dumps() else it will result in an error being returned
    response = requests.post(url, data=json.dumps(data), headers=headers).json()

    # The response object does not have the "result" key if it's reporting an error so if
    # we cannot return that value we likely got an error returned
    try:
        return response["result"]

    except KeyError:
        if response["error"]:
            logging.error('Error: {num}\nMessage: {Message}'.format(num=response['error']['code'],
                                                                    Message=response['error']['message']))
            return False


def calculate_rate(con_speed=None, rate="unlimited"):

    # Assign percent values to each rate limit tier which is used to calculate the new limit
    rate_limits = dict(unlimited=0,
                       high=0.80,
                       medium=0.55,
                       low=0.25,
                       crawl=0.01)

    if rate not in rate_limits.keys():
        logging.warning("Invalid rate given, defaulting to Unlimited")

    elif rate == "unlimited":
        return 0

    else:
        # NZBGet sets the rate in KBps(Kilobytes per second) while most humans use Mbps(Megabits per second) so
        # we set our connection_speed in Mbps and then convert the new rate to KBps
        new_rate = math.floor((((con_speed * rate_limits[rate]) / 8) * 1024))
        return new_rate


def monitor(Config, logging=logging):
    plexpy_base_url = Config.get('plexpy', 'url')
    plexpy_apikey = Config.get('plexpy', 'apikey')

    # NZBGet configs
    nzb_base_url = Config.get('nzbget', 'url')
    nzb_username = Config.get('nzbget', 'user')
    nzb_password = Config.get('nzbget', 'password')

    # TODO: Look into implementing a dynamic check interval based on active streams. More streams = more frequent checks
    check_interval = int(Config.get('nzbandwidth', 'check_interval'))
    connection_speed = int(Config.get('nzbandwidth', 'connection_speed'))

    logging.info("Starting NZBGet Rate Limiter")

    prev_stream_count = None

    while True:
        # Get Plex's active streams data using Plexpy's API
        # There is tons of potentially useful data included that may be used in the future to calculate
        # the speed limit more dynamically based on other metrics like the video quality
        activity = plexpy_get_activity(plexpy_base_url, plexpy_apikey)

        if activity is None:
            logging.warning('Failed to get activity data from PlexPy, skipping')
            pass

        stream_count = int(activity['stream_count'])
        logging.debug('Stream Count: {}'.format(stream_count))

        # Check if there was any change in the number of streams to prevent making unneeded calls to NZBGet
        if stream_count == prev_stream_count:
            logging.info("Stream count unchanged, skipping")
            pass

        else:
            logging.debug('Previous Stream Count: {}'.format(prev_stream_count))

            # Figure out the new speed limit to be applied based on the stream count and the servers connection speed
            if stream_count == 0:
                new_rate = calculate_rate(connection_speed, "unlimited")
            elif stream_count == 1:
                new_rate = calculate_rate(connection_speed, "high")
            elif 2 <= stream_count < 4:
                new_rate = calculate_rate(connection_speed, "medium")
            elif 4 <= stream_count < 6:
                new_rate = calculate_rate(connection_speed, "low")
            elif stream_count >= 6:
                new_rate = calculate_rate(connection_speed, "crawl")
            else:
                # Should only act on positive integers, anything else should be skipped/ignored
                logging.warning("Stream count out of range {cnt}, Skipping".format(cnt=stream_count))
                pass

            # Set the new download speedlimit in NZBGet
            set_rate_result = nzbget_set_rate(nzb_base_url, nzb_username, nzb_password, rate=new_rate)

            if set_rate_result is True:
                logging.info("New rate limit: {rate} KB/s".format(rate=new_rate))
                prev_stream_count = stream_count

            else:
                logging.error("Error setting rate")
                pass

        logging.debug('Sleeping for {} seconds'.format(check_interval))
        sleep(check_interval)

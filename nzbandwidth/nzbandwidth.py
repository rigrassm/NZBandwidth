#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import requests
from time import sleep
import json


# TODO: Move these options to separate configuration file
########################################################################################################################
# Config Options
########################################################################################################################

# PlexPy Connection details
plexpy_base_url = "https://plexpy.example.com"
plexpy_apikey = "ashf511hjsfgafgh1d5as5dfg4a5s"

# NZBGet connection details
nzb_base_url = "https://nzb.example.com"
nzb_username = "nzbadmin"
nzb_password = "tegbzn"

# Define maximum connection speed in Mbps for rate limit calculations
# Suggest running a speed test at different times to obtain an average real download speed
connection_speed = 600

# Check interval is the number of seconds between calls to the PlexPy checking for active streams
# TODO: Look into implementing a dynamic check interval based on active streams. More streams = more frequent checks
check_interval = 30

########################################################################################################################


def plexpy_get_activity():
    url = '{base_url}/api/v2'.format(base_url=plexpy_base_url)
    params = dict(apikey=plexpy_apikey,
                  cmd="get_activity"
                  )
    # TODO: Look at PlexPy's return data for errors and handle these accordingly
    try:
        response = requests.get(url, params=params).json()
        return response["response"]["data"]
    except KeyError:
        return None


def nzbget_set_rate(rate=0):

    # Build a JSON-RPC compatible object which tells nzb what to set the speed limit to
    data = dict(method="rate", params=rate, jsonrpc="2.0", id=0)
    headers = {'content-type': 'application/json'}
    url = "{base_url}/{user}:{passwd}/jsonrpc".format(base_url=nzb_base_url,
                                                      user=nzb_username,
                                                      passwd=nzb_password).encode('utf-8')

    # Send our request, data dict object must be run through json.dumps() else it will result in an error being returned
    response = requests.post(url, data=json.dumps(data), headers=headers).json()

    # The response object does not have the "result" key if it's reporting an error so if
    # we cannot return that value we likely got an error returned
    try:
        return response["result"]

    except KeyError:
        if response["error"]:
            print('Error: {num}\nMessage: {Message}'.format(num=response['error']['code'],
                                                            Message=response['error']['message']))
            return False


def calculate_rate(rate="unlimited"):
    # Assign percent values to each rate limit tier which is used to calculate the new limit
    rate_limits = dict(unlimited=0,
                       high=0.80,
                       medium=0.55,
                       low=0.25,
                       crawl=0.01)

    if rate not in rate_limits.keys():
        print("Invalid rate given, defaulting to Unlimited")

    elif rate == "unlimited":
        return 0

    else:
        # NZBGet sets the rate in KBps(Kilobytes per second) while most humans use Mbps(Megabits per second) so
        # we set our connection_speed in Mbps and then convert the new rate to KBps
        new_rate = round((((connection_speed * rate_limits[rate]) / 8) * 1024))
        return new_rate


def main():
    print("Starting NZBGet Rate Limiter")
    prev_stream_count = None

    while True:
        # Get Plex's active streams data using Plexpy's API
        # There is tons of potentially useful data included that may be used in the future to calculate
        # the speed limit more dynamically based on other metrics like the video quality
        activity = plexpy_get_activity()
        if activity is None:
            print('Failed to get activity data from PlexPy, skipping')
            pass

        stream_count = int(activity['stream_count'])

        # Check if there was any change in the number of streams to prevent making unneeded calls to NZBGet
        if stream_count == prev_stream_count:
            print("Stream count unchanged, skipping")
            pass

        else:
            # Figure out the new speed limit to be applied based on the stream count and the servers connection speed
            if stream_count == 0:
                new_rate = calculate_rate("unlimited")
            elif stream_count == 1:
                new_rate = calculate_rate("high")
            elif 2 <= stream_count < 4:
                new_rate = calculate_rate("medium")
            elif 4 <= stream_count < 6:
                new_rate = calculate_rate("low")
            elif stream_count >= 6:
                new_rate = calculate_rate("crawl")
            else:
                # Should only act on positive integers, anything else should be skipped/ignored
                print("Stream count out of range {cnt}, Skipping".format(cnt=stream_count))
                pass

            set_rate_result = nzbget_set_rate(rate=new_rate)

            if set_rate_result is True:
                print("New rate limit: {rate} KB/s".format(rate=new_rate))
                prev_stream_count = stream_count

            else:
                print("Error setting rate")
                pass

        sleep(check_interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping service")

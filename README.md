# NZBandwidth
Application for automatically limiting NZBGet download bandwidth based on the number of active Plex streams

## Configuration

### Configuration file

    /path/to/NZBandwidth/nzbandwidth/config.ini

#### PlexPy Config Options
* url = "https://plexpy.example.com"
* plexpy_apikey = "as98df7a8sdfa998as7d8fa9d7f88a"

#### NZBGet Config Options
* nzb_base_url = "https://nzb.example.com"
* nzb_username = "nzbadmin"
* nzb_password = "tegbzn"

#### NZBandwidth Config Options
Connection speed is your servers max download speed in Mbps(Megabits per second)
* connection_speed = 600

Check interval is the amount of time to wait between checking PlexPy for activity data
* check_interval = 30

Set the log level and location of the logfile
* log_file: /path/to/nzbandwidth.log
* log_level: [info, debug]

Daemonize the processes
* daemon: [true, false]

## Usage
    python nzbandwidth.py

## Coming Soon
* Command line argument parsing
* Add ability to run as a background daemon
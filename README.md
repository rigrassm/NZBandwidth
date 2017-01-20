# NZBandwidth
Application for automatically limiting NZBGet download bandwidth based on the number of active Plex streams

## Configuration

#### PlexPy API Connection Details
* plexpy_base_url = "https://plexpy.example.com"
* plexpy_apikey = "as98df7a8sdfa998as7d8fa9d7f88a"

#### NZBGet API Connection Details
* nzb_base_url = "https://nzb.example.com"
* nzb_username = "nzbadmin"
* nzb_password = "tegbzn"

#### NZBandwidth Configurations
Connection speed is your servers max download speed in Mbps(Megabits per second)
* connection_speed = 600

Check interval is the amount of time to wait between checking PlexPy for activity data
* check_interval = 30

## Usage
    python nzbandwidth.py

## Coming Soon
* Proper configuration file and command line argument parsing
* Implement proper logging with standard and debug levels
* Add ability to run as a background daemon
# -*- coding: utf-8 -*-

import glob
import requests
import json
import math
import time
from datetime import datetime 
from datetime import timedelta 
import locale
import argparse
from inky import inky_display
from PIL import ImageFont
from font_fredoka_one import FredokaOne
from enum import Enum
locale.setlocale(locale.LC_TIME,'')
folder_img = '/home/pi/Documents/images/'
try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
darksky_api_key = "/0c364b329eaaaf21879e82272fbb2cba"
darksky_forecast_url = "https://api.darksky.net/forecast"
durham_lat_lon = "/35.5915,-78.5426"

# Set up the display

inky_display = inky_display("red")
inky_display.set_border(inky_display.RED)

# Details to customise your weather display

CITY = "Durham, NC"
COUNTRYCODE = "US"
WARNING_TEMP = 25.0

traffic_checker_url = "http://spconrad.com/trafficchecker/justtime"

def get_travel_time_to_office():
    r = requests.get(traffic_checker_url)
    if r.status_code == 200:
        return r.text
    else:
        return "Dunno"

# Query the Dark Sky weather API to get current weather data
def get_weather():
    r = requests.get(darksky_forecast_url + darksky_api_key + durham_lat_lon)    
    if r.status_code == 200:
        json_data = json.loads(r.text)
        return json_data

    return {}

# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)

display_pressure_text = ""
display_pressure_color = 0

# Load the FredokaOne font
font = ImageFont.truetype(FredokaOne, 22)
WARNING_TEMP = 90
def updateFrame():
     weather = get_weather()
    t = weather["currently"]["temperature"]
    h = weather["currently"]["Humidity"]
    commute = get_travel_time_to_office()
    commuteTime = int(commute[:2])
    #timestamp
    ts = datetime.datetime.now() # timestamp
    ts0 ='{:%Y-%m-%d}'.format(ts) # timestamp - date, EN format
    ts1='{:%H:%M:%S}'.format(ts) # timestamp - time
    tmp = "{0:0.1f}".format(t)
    hum = "{0:0.1f}".format(h)
    tText = "Temp.: "   
    hText = "Humidity: "
    travelText = "Commute Time: "

    image = inky_display.Image.new('P', (inky_display.WIDTH, inky_display.HEIGHT))

    draw = ImageDraw.Draw(image)


    travel_time = get_travel_time_to_office()
    travel_time_int = int(travel_time[:2])
    if travel_time_int > 20:      
        travel_time_color = 2
    else:
        travel_time_color = 0

    # print values to Inky pHAT
    t1 = 5   # tab 1, frist column, simplifies optimization of layout
    t2 = 110 # tab 2, second column
   
    
    draw.text((t1, 0), ts0, inky_display.BLACK, font2) # write timestamp date
    draw.text((t2, 0), ts1, inky_display.BLACK, font2) # write timestamp time
    draw.line ((t1,25, 207,25), 1,3)  # draw a line
    
    draw.text((t1, 30), tText, inky_display.BLACK, font2)
    draw.text((t2, 30), (tmp + "°C"), inky_display.BLACK, font2)
    draw.text((t1, 55), hText, inky_display.BLACK, font2)
    draw.text((t2, 55), (hum + " %"), inky_display.BLACK, font2)
    draw.text((t1, 80), travelText, inky_display.BLACK, font2)
    draw.text((t2, 80), (commuteTime + " %"), travel_time_color, font2)

    inky_display.show()
    time.sleep(51) # wait some seconds before next measurements, +19 sec per cycle

    inky_display.set_image(img)
    inky_display.show()

    
def main():
    while True:
        time.sleep(600)
        updateFrame()

if __name__ == "__main__":
    updateFrame()
    main()




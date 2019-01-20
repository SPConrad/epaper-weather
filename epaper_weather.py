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
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
from enum import Enum
locale.setlocale(locale.LC_TIME,'')
folder_img = '/home/pi/Documents/images/'
try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

degree_sign= u'\N{DEGREE SIGN}'

class Icons(Enum):
    snow = "snow"
    rain = "rain"
    fog = "fog"
    cloudy = "cloudy"
    partly_cloudy_night = "cloudy"
    partly_cloudy_day = "cloudy"
    storm = "storm"
    clear_day = "clear-day"
    clear_night = "clear-night"
    wind = "wind"

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
darksky_api_key = "/0c364b329eaaaf21879e82272fbb2cba"
darksky_forecast_url = "https://api.darksky.net/forecast"
durham_lat_lon = "/35.5915,-78.5426"
parser = argparse.ArgumentParser()

args = parser.parse_args()


# Set up the display

inky_display = InkyPHAT("red")
inky_display.set_border(inky_display.RED)

# Details to customise your weather display

CITY = "Durham, NC"
COUNTRYCODE = "US"
WARNING_TEMP = 25.0

#wind
#icon-wind

#clear-day, clear-night
#icon-clear

#rain
#icon-rain

#fog
#icon-fog

#snow
#icon-snow

#cloudy, partly-cloudy-day, partly-cloudy-night
#icon-cloudy

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
        print(json_data["currently"]["summary"])
        print(json_data["currently"]["temperature"])
        print(json_data["hourly"]["summary"])
        return json_data

    return {}


def create_mask(source, mask=inky_display.RED):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            mask_image.putpixel((x, y), 255)

    return mask_image


# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)

# Load our icon files and generate masks
for icon in glob.glob("resources/icon-*.png"):
    icon_name = icon.split("icon-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

display_pressure_text = ""
display_pressure_color = 0

# Load the FredokaOne font
font = ImageFont.truetype(FredokaOne, 22)
WARNING_TEMP = 90
def updateFrame():
    weather = get_weather()
    temperature = weather["currently"]["temperature"]
##    pressure = weather["currently"]["pressure"]
    summary = weather["currently"]["icon"]
    if "-" in summary:
        summary = summary.replace("-", "_")
    
    img = Image.open("/home/pi/Documents/resources/backdrop.png")
    draw = ImageDraw.Draw(img)
    
    # Draw lines to frame the weather data
    draw.line((69, 36, 69, 81))       # Vertical line
    draw.line((31, 35, 184, 35))      # Horizontal top line
    draw.line((69, 58, 174, 58))      # Horizontal middle line
    draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D

    # Write text with weather values to the canvas
    datetime = time.strftime("%d/%m %H:%M")
    
    draw.text((36, 12), datetime, inky_display.WHITE, font=font)

    draw.text((72, 34), "T", inky_display.WHITE, font=font)
    draw.text((92, 34), u"{:.0f}°".format(temperature), inky_display.WHITE if temperature < WARNING_TEMP else inky_display.RED, font=font)

##    draw.text((72, 58), "P", inky_display.WHITE, font=font)
    
##    if pressure > 1020:
##        display_pressure_text = "HIGH"        
##        display_pressure_color = 0
##    elif pressure < 988:
##        display_pressure_text = "LOW"
##        display_pressure_color = 2
##    else:
##        display_pressure_text = "Norm"
##        display_pressure_color = 0
    
##    draw.text((92, 58), display_pressure_text, display_pressure_color, font=font)

    travel_time = get_travel_time_to_office()
    travel_time_int = int(travel_time[:2])
    if travel_time_int > 20:      
        travel_time_color = 2
    else:
        travel_time_color = 0

    draw.text((72, 58), travel_time, travel_time_color, font=font)
    
    icon_string = Icons[summary].value
    if summary is not None:
        img.paste(icons[icon_string], (28, 36), masks[icon_string])

    inky_display.set_image(img)
    inky_display.show()

    
def main():
    while True:
        time.sleep(600)
        updateFrame()

if __name__ == "__main__":
    updateFrame()
    main()





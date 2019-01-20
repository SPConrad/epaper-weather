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
parser = argparse.ArgumentParser()
parser.add_argument('--colour', '-c', type=str, required=True, choices=["red", "black", "yellow"], help="ePaper display colour")
args = parser.parse_args()


# Set up the display

colour = args.colour
inky_display = InkyPHAT(colour)
inky_display.set_border(inky_display.RED)

# Details to customise your weather display

CITY = "Durham, NC"
COUNTRYCODE = "US"
WARNING_TEMP = 25.0

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


def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
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
            if p in mask:
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

# Load the FredokaOne font
font = ImageFont.truetype(FredokaOne, 22)
WARNING_TEMP = 35
def updateFrame():
    weather = get_weather()
    temperature = weather["currently"]["temperature"]
    pressure = weather["currently"]["pressure"]

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
    draw.text((92, 34), u"{:.2f}*".format(temperature), inky_display.WHITE if temperature < WARNING_TEMP else inky_display.RED, font=font)

    draw.text((72, 58), "P", inky_display.WHITE, font=font)
    draw.text((92, 58), "{}".format(pressure), inky_display.WHITE, font=font)

    inky_display.set_image(img)
    inky_display.show()





def main():
    while True:
        time.sleep(600)
        get_weather()
        updateFrame()

if __name__ == "__main__":
    get_weather()
    updateFrame()
    main()





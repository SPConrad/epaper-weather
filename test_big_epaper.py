#!/usr/bin/python
# -*- coding:utf-8 -*-
# sudo apt-get install ttf-aenigma fonts-tuffy
import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

ORIENTATION = "horizontal"

# This is a black and white display, 1-bit only 
IMAGE_MODE = '1'

# degree symbol °

HEIGHT = 176
WIDTH = 264

CLEAR = 255
FONT_SIZE = 20

epd = epd2in7.EPD()

FONT = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', FONT_SIZE)


def init():
    print("Hello main")
    epd.init()
    epd.clear(0xFF)

    image = blankCanvas()

    writeToDisplay()


def writeToDisplay():
    temp = 70
    humidity = 25
    commuteTime = 18
    print("Hello writeToDisplay")
    draw = ImageDraw.Draw(image)
    draw.text((10, 0), 'Temp: %s°' % temp, font = FONT)
    draw.text((10, 20), 'Humidity: %s%' % humidity, font = FONT)
    draw.text((10, 40), 'Commute Time: %s' % commuteTime, font = FONT)

    epd.display(epd.getBuffer(image))



def blankCanvas():
    return Image.new(IMAGE_MODE, (HEIGHT, WIDTH), CLEAR)

def loop():
    init()
    delay(100)
'''
This micropython script will make regular requests to the cheerlights api
and parse out the latest 'color' information using the
'ujson' method. 
A counter is reset with each new color and incremented with each
subsequent same color cycle.

@author George Kaimakis and Russ Winch
@version 3 Dec 2017
'''

import urequests
import time
import neopixel
from machine import Pin
from wifi import Wifi

# Global variables:
RECVD_COLOR         = ''
PREVIOUS_COLOR      = ''
NEW_COLOR_VAL       = ''
OLD_COLOR_VAL       = ''
PIXEL_PIN           = 0
NUM_OF_PIXELS       = 4

INTERVAL            = 10000

host                = 'https://thingspeak.com/'
topic               = 'channels/1417/feeds/last.json'
api                 = host + topic


# look-up color dict - api 'field1' is used as the key:
colors = {
    'red':(255,0,0),
    'orange':(255,30,0),
    'yellow':(255,110,1),
    'green':(0,255,0),
    'cyan':(0,255,255),
    'blue':(0,0,255),
    'purple':(128,0,128),
    'magenta':(255,0,50),
    'pink':(255,40,50),
    'white':(255,255,170),
    'oldlace':(255,150,50),
    'warmwhite':(255,150,50)
    }

def api_request(url):
    global RECVD_COLOR
    feed = urequests.get(url)
    color = feed.json()['field1']
    RECVD_COLOR = color

def recvd_color_test(color):
    global NEW_COLOR_VAL
    if color in colors:
        NEW_COLOR_VAL = colors[color]

def new_neopixel_color(next_color):
    np.fill(next_color)
    np.write()

def neopixel_blank():
    np.fill((0,0,0))
    np.write()

def color_transition():
    global NEW_COLOR_VAL
    global OLD_COLOR_VAL

# define pin and create neopixel object:
pin = Pin(PIXEL_PIN, Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_OF_PIXELS)

# turn off any lit neopixels:
neopixel_blank()

wifi = Wifi()
wifi.connect()

count = 0
while True:
    api_request(api)

    # Check if color has changed:
    # -if color is unchanged, increment counter, print and continue
    if RECVD_COLOR == PREVIOUS_COLOR:
        count += 1
        print(str(count) + ': ' + RECVD_COLOR)

    # -if color has changed, reset counter, print, extract colot value form dict
    # -and regenerate neopixel with new color.
    # -reset color varaiables
    else:
        count = 1
        print(str(count) + ': ' + RECVD_COLOR)
        recvd_color_test(RECVD_COLOR)
        new_neopixel_color(NEW_COLOR_VAL)
        PREVIOUS_COLOR = RECVD_COLOR
        OLD_COLOR_VAL = NEW_COLOR_VAL
    time.sleep_ms(INTERVAL)

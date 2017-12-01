# This micropython script will make a request to the cheerlights api
# every 20 seconds and parse out the latest 'color' information using the
# 'ujson' method. 
# A counter is reset with each new color and incremented with each
# subsequent same color cycle.

# Author: George Kaimakis
# This file was created on 13/02/17


import urequests
import time
import neopixel
import machine

# Global variables:
RECVD_COLOR         = ''
PREVIOUS_COLOR      = ''
PIXEL_PIN           = 0
NUM_OF_PIXELS       = 4
NEW_COLOR_VAL       = ''
OLD_COLOR_VAL       = ''

INTERVAL            = 20000

host                = 'https://thingspeak.com/'
topic               = 'channels/1417/feeds/last.json'
api                 = host + topic


# look-up color dict - api 'field1' is used as the key:
colors = {'red':(255,0,0), 'orange':(255, 30, 0), 'yellow':(254,183,12),
'green':(0,128,0), 'cyan':(0,255,255), 'blue':(0,0,255), 'purple':(128,0,128),
'magenta':(255,0,255), 'pink':(254,52,62), 'white':(255,255,230),
'oldlace':(255,200,130), 'warmwhite':(255,200,130)}

def api_request(url):
    global RECVD_COLOR
    feed = urequests.get(url)
    color = feed.json()['field1']
    RECVD_COLOR = color
    return None

def recvd_color_test(color):
    global NEW_COLOR_VAL
    if color in colors:
        NEW_COLOR_VAL = colors[color]
    return None

def new_neopixel_color(next_color):
    np.fill(next_color)
    np.write()
    return None

def neopixel_blank():
    np.fill((0,0,0))
    np.write()
    return None

def color_transition():
    global NEW_COLOR_VAL
    global OLD_COLOR_VAL
    pass

# define pin and create neopixel object:
pin = machine.Pin(PIXEL_PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_OF_PIXELS)

# turn off any lit neopixels:
neopixel_blank()

count = 0

def to_int(string):
    integer = []
    for i in string:
        integer.append(int(i))
    return integer

while True:
    # api_request(api)
    

    # Check if color has changed:
    # -if color is unchanged, increment counter, print and continue
    # if RECVD_COLOR == PREVIOUS_COLOR:
    #     count += 1
    #     print(str(count) + ': ' + RECVD_COLOR)
    
    # color = input('colour > ')
    rgb = input('RGB >')
    # print(rgb)
    rgb = rgb.split(' ')
    if len(rgb) == 1:
        color = colors[rgb[0]]
        print(color)
        new_neopixel_color(color)
        
    elif len(rgb) == 3:
        color = to_int(rgb)
        new_neopixel_color(color)
    else:
        print('invalid entry!')
    # print(rgb)
    # r, g, b = rgb.split(' ')
    # color = (int(r), int(g), int(b))
    # color = to_int(rgb)
    # new_neopixel_color(color)

    # new_neopixel_color(colors[color])

    # -if color has changed, reset counter, print, extract colot value form dict
    # -and regenerate neopixel with new color.
    # -reset color varaiables
    # else:
    #     count = 1
    #     print(str(count) + ': ' + RECVD_COLOR)
    #     recvd_color_test(RECVD_COLOR)
    #     new_neopixel_color(NEW_COLOR_VAL)
    #     PREVIOUS_COLOR = RECVD_COLOR
    #     OLD_COLOR_VAL = NEW_COLOR_VAL
    # time.sleep_ms(INTERVAL)

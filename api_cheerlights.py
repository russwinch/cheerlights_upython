'''
This micropython script will make regular requests to the cheerlights api
and parse out the latest 'color' information using the
'ujson' method. 
A counter is reset with each new color and incremented with each
subsequent same color cycle.

@author George Kaimakis and Russ Winch
@version December 2017
'''

import urequests
import time
import urandom
import neopixel
from machine import Pin
from wifi import Wifi

def api_request(url):
    feed = urequests.get(url)
    return feed.json()['field1']

def recvd_color_test(color, colors):
    if color in colors:
        return colors[color]
    print("not a valid Cheerlights colour")
    return colors['red'] # default to red

def new_neopixel_color(neo, next_color):
    for i in range(len(neo)):
        neo[i].fill(next_color)
        neo[i].write()
        time.sleep_ms(urandom.getrandbits(11)) # randomise transition

def neopixel_blank(neo):
    for i in range(len(neo)):
        neo[i].fill((0,0,0))
        neo[i].write()

# def color_transition():
#     global NEW_COLOR_VAL
#     global OLD_COLOR_VAL

def main():
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

    recvd_color     = ''
    prev_color      = ''
    # NEW_COLOR_VAL       = ''
    # OLD_COLOR_VAL       = ''

    interval            = 15 # seconds delay between updates

    host                = 'https://thingspeak.com/'
    topic               = 'channels/1417/feeds/last.json'
    api                 = host + topic

    neopixels   = [] # holder for the neo pixels
    pixel_pins  = [0,14,12,13,15] # D3,D5,D6,D7,D8
    num_pixels  = 1 # leds per strip

    # define pins and create neopixel objects:
    for i in range(len(pixel_pins)):
        pin = Pin(pixel_pins[i], Pin.OUT)
        neopixels.append(neopixel.NeoPixel(pin, num_pixels))

    # turn off any lit neopixels:
    neopixel_blank(neopixels)

    # connect wifi
    wifi = Wifi()
    wifi.connect()

    count = 0

    while True:
        recvd_color = api_request(api)

        # Check if color has changed:
        if recvd_color == prev_color:
            count += 1
            print(str(count) + ': ' + recvd_color)

        # if color has changed, reset counter, print, extract color from dict
        else:
            count = 1
            print(str(count) + ': ' + recvd_color)
            prev_color = recvd_color
            recvd_color = recvd_color_test(recvd_color, colors)
            new_neopixel_color(neopixels, recvd_color)

        # sleep till the next update
        time.sleep(interval)

# run the main function
if __name__ == "__main__":
    main()

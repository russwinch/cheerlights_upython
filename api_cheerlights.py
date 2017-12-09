'''
This micropython script will make regular requests to the cheerlights api
and parse out the latest 'color' information using the
'ujson' method. 
A counter is reset with each new color and incremented with each
subsequent same color cycle.

@author George Kaimakis and Russ Winch
@version December 2017
'''

import time
import urequests
import urandom
import neopixel
from machine import Pin, ADC
from wifi import Wifi

def api_request(url):
    feed = urequests.get(url)
    return feed.json()['field1']

def recvd_color_test(color, colors):
    """check for the color and returns RGB values"""
    if color in colors:
        return colors[color]
    print("not a valid Cheerlights colour")
    return colors['red'] # default to red

def new_neopixel_color(neo, next_color, colors):
    color = recvd_color_test(next_color, colors)
    return color

def neopixel_write(neo, color, *args):
    if len(args) == 1:
        i = args[0]
        neo[i].fill(color)
        neo[i].write()
    # ignore none or too many arguments
    else:
        for i in range(len(neo)):
            neo[i].fill(color)
            neo[i].write()

def neopixel_blank(neo):
    neopixel_write(neo, (0,0,0))

def neopixel_confirm(neo, value, colors):
    if type(value) != bool:
        print("not a boolean value")
    if value == True:
        color = colors['green']
    else:
        color = colors['red']
    for i in range(3):
        # flash 3 times
        delay = 300 # ms
        neopixel_write(neo, color)
        time.sleep_ms(delay)
        neopixel_blank(neo)
        time.sleep_ms(delay)

def color_transition(neo, previous, target):
    """compares previous and target rgb values & calculates the transition.
    writes to the neopixel & returns the current value as previous.
    """
    if target != previous:
        for i, j in enumerate(previous):
            if previous[i] < target[i]:
                previous[i] += 1
            elif previous[i] > target[i]:
                previous[i] -= 1
        neopixel_write(neo, previous)
    time.sleep_ms(30)
    return previous


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


    host  = 'https://thingspeak.com/'
    topic = 'channels/1417/feeds/last.json'
    api   = host + topic

    neopixels   = [] # holder for the neo pixels
    pixel_pins  = [0,14,12,13,15] # D3,D5,D6,D7,D8
    num_pixels  = 1 # leds per strip

    # define pins and create neopixel objects:
    for i in range(len(pixel_pins)):
        pin = Pin(pixel_pins[i], Pin.OUT)
        neopixels.append(neopixel.NeoPixel(pin, num_pixels))

    # turn off any lit neopixels:
    neopixel_blank(neopixels)

    # seed the random generator
    adc = ADC(0)
    seed = adc.read()
    print("random seed: ", seed)
    urandom.seed(seed)

    # connect wifi
    wifi = Wifi()
    online = wifi.connect()
    neopixel_confirm(neopixels, online, colors)

    count = 0
    prev_color = ''
    previous_rgb = ()
    target_rgb = ()
    interval = 15 # seconds delay between updates
    last_update = time.time() + interval

    while True:
        if time.time() > last_update + interval:
            recvd_color = api_request(api)
            last_update = time.time()

        # Check if color has changed:
        if recvd_color == prev_color:
            count += 1
            print(str(count) + ': ' + recvd_color)

        # if color has changed, reset counter, print, extract color from dict
        else:
            count = 1
            print(str(count) + ': ' + recvd_color)
            prev_color = recvd_color
            target_rgb = new_neopixel_color(neopixels, recvd_color, colors)

        previous_rgb = color_transition(neopixels, previous_rgb, target_rgb)

        # sleep till the next update
        # time.sleep(interval)

# run the main function
if __name__ == "__main__":
    main()

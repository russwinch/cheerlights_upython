"""
This micropython script will make regular requests to the cheerlights api
and parse out the latest 'color' information using the
'ujson' method. 
A counter is reset with each new color and incremented with each
subsequent same color cycle.

@authors George Kaimakis and Russ Winch
@version December 2017
"""

import gc
import sys
import time
import urequests
import urandom
import neopixel
from machine import Pin, ADC

try:
    from wifi import Wifi
except ImportError:
    print()
    print("'wifi' module not found.")
    print()

def api_request(url):
    feed = urequests.get(url)
    return feed.json()['field1']

def new_neopixel_color(color, colors):
    """check the color is valid and return RGB values"""
    if color in colors:
        return colors[color]
    print("not a valid Cheerlights colour")
    return colors['red'] # default to red

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
    """This function determines the return value from the wifi() call and
    flashes the neopixels accordingly, green for wifi success, and red for wifi failure
    or for an invalid bool return.
    """
    if value == True:
        color = colors['green']
        np_flash(neo, color)    # uses default kwargs
        return True
    elif value == False:
        color = colors['red']
        np_flash(neo, color)    # uses default kwargs
        return False
    else:
        print("Not a boolean value!")
        color = colors['purple']
        np_flash(neo, color, num_of_flashes=6, duration=150)
        return False

def np_flash(neo, color,  *, num_of_flashes=3, duration=300):
    """This function flashes the neopixel(s) in terms of number of flashes and
    duration value in milliseconds.
    Note: function accepts keyword-only arguments.
    """
    for i in range(num_of_flashes):
        neopixel_write(neo, color)
        time.sleep_ms(duration)
        neopixel_blank(neo)
        time.sleep_ms(duration)

def color_transition(neo, previous, target):
    """compares previous and target rgb values & calculates the transition.
    writes to the neopixel & returns the new color value to the caller to be
    asigned as the next previous_rgb value.
    """
    speed = 25 # ms delay after each transition
    new = list(previous)
    if target != previous:
        for i, _ in enumerate(previous):
            if previous[i] < target[i]:
                new[i] += 1
            elif previous[i] > target[i]:
                new[i] -= 1
        neopixel_write(neo, new)
    time.sleep_ms(speed) # smooth the transition
    return tuple(new)


def main():
    # look-up color dict - api 'field1' is used as the key:
    colors = {
        'red':          (255, 0, 0),
        'orange':       (255, 30, 0),
        'yellow':       (255, 110, 1),
        'green':        (0, 255, 0),
        'cyan':         (0, 255, 255),
        'blue':         (0, 0, 255),
        'purple':       (128, 0, 128),
        'magenta':      (255, 0, 50),
        'pink':         (255, 40, 50),
        'white':        (255, 255, 170),
        'oldlace':      (255, 150, 50),
        'warmwhite':    (255, 150, 50)
        }


    host  = 'https://thingspeak.com/'
    topic = 'channels/1417/feeds/last.json'
    api   = host + topic

    neopixels   = [] # holder for the neo pixels
    pixel_pins  = [12] # D3
    num_pixels  = 1 # leds per strip

    # define pins, create neopixel objects, and populate neopixels list:
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

    # attempt to connect to wifi - call neopixel_confirm() with wifi bool response.
    # if connected, break from while loop:
    try:
        wifi = Wifi()
        while not wifi.net.isconnected():
            online = wifi.connect()
            if wifi.net.isconnected: # True
                online = wifi.net.isconnected()
                neopixel_confirm(neopixels, online, colors)
                print("online is:", online)
                print("online!")
                break
            neopixel_confirm(neopixels, online, colors)
            print("offline!")
    except NameError:
        print()
        print("'wifi' object could not be created.\n" \
                "Please check and re-boot.\n" \
                "Exiting..!")
        print()
        sys.exit()
    online = wifi.net.isconnected()
    print("online:", online)
    neopixel_confirm(neopixels, online, colors)
    print("already connected.\nstarting up...\n")

    prev_color   = ''
    previous_rgb = (0, 0, 0)
    recvd_color  = ''
    target_rgb   = (0, 0, 0)

    count = 0
    interval = 15 # seconds delay between updates
    last_update = time.time() - interval
    # last_update = -100 # time.time() + interval

    # main loop:
    while True:
        if time.time() > last_update + interval:
            recvd_color = api_request(api)
            last_update = time.time()

            # If cheerlights color feed has changed, increment counter:
            if recvd_color == prev_color:
                count += 1

            # if color has changed, reset counter, re-assign prev_color,
            # extract rgb color from color lookup dict:
            else:
                count = 1
                prev_color = recvd_color
                target_rgb = new_neopixel_color(recvd_color, colors)

            print(str(count) + ': ' + recvd_color)

        previous_rgb = color_transition(neopixels, previous_rgb, target_rgb)

# run the main function
if __name__ == "__main__":
    main()

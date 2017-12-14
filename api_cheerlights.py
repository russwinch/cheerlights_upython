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

class Cheerlight(object):
    def __init__(self, pin, num_pixels):
        self.neo = neopixel.NeoPixel(pin, num_pixels)
        self.color = (0, 0, 0) # current colour rgb
        self.target = (0, 0, 0) # target colour rgb
        self.delay = 0 # delay before changing

    def write(self, color):
        ''' write to a NeoPixel '''
        self.neo.fill(color)
        self.neo.write()
        self.color = color

    def blank(self):
        ''' turn the NeoPixel off '''
        self.write(0, 0, 0)

    def new_color(self, color_name, colors):
        ''' check and convert incoming colour to RGB value and set delay before
        the colour is changed '''
        if color_name in colors:
            self.target = colors[color_name]
        self.delay = time.time() + random.getrandbits(10)
        print("delay set to: ", self.delay)

    def transition(self):
        ''' check if the NeoPixel is in sync with the target and iterate to the
        target colour if not '''
        if self.color != self.target and time.time() > self.delay:
            new = list(self.color)
            for i, _ in enumerate(self.color):
                if self.color[i] < self.target[i]:
                    new[i] += 1
                elif self.color[i] > self.target[i]:
                    new[i] -= 1
            self.write(new)

def api_request(url):
    ''' retrieve the webpage and extract field1 from the json. Contains the name
    of the Cheerlights colour '''
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

def multi_cheerlight_write(neo, color, *args):
    ''' write to a specified cheerlight or iterate through and write to all of
    them '''
    if len(args) == 1:
        i = args[0]
        neo[i].fill(color)
        neo[i].write()
    # ignore none or too many arguments
    else:
        for i in range(len(neo)):
            neo[i].fill(color)
            neo[i].write()

def multi_cheerlight_transitition(neo):
    ''' iterate through all connected cheerlights triggering the transition
    method '''
    for i, _ in enumerate(neo):
        neo.transition()
        time.sleep_ms(200)

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
    pixel_pins  = [0,14,12,13,15] # D3,D5,D6,D7,D8
    num_pixels  = 1 # leds per strip

    # define pins and create neopixel objects:
    for i in range(len(pixel_pins)):
        pin = Pin(pixel_pins[i], Pin.OUT)
        neo = Cheerlight(0, num_pixels)
        # neopixels.append(Cheerlight(pin, num_pixels))
        # neopixels.append(neopixel.NeoPixel(pin, num_pixels))

    # turn off any lit neopixels:
    # neopixel_blank(neopixels)

    # seed the random generator from the analog pin
    adc = ADC(0)
    seed = adc.read()
    print("random seed: ", seed)
    urandom.seed(seed)

    # connect wifi
    wifi = Wifi()
    online = wifi.connect()
    # neopixel_confirm(neopixels, online, colors)

    prev_color   = ''
    previous_rgb = (0, 0, 0)
    recvd_color  = ''
    target_rgb   = ()

    count = 0
    interval = 15 # seconds delay between updates
    last_update = -100 # time.time() + interval

    while True:
        if time.time() > last_update + interval:
            recvd_color = api_request(api)
            last_update = time.time()

            # Check if color has changed:
            if recvd_color == prev_color:
                count += 1

            # if color has changed, reset counter, print, extract color from dict
            else:
                count = 1
                prev_color = recvd_color

                neo.new_color(recvd_color, colors)
                neo.write(neo.target)
                # target_rgb = new_neopixel_color(recvd_color, colors)
                # for i, _ in enumerate(neopixels):
                    # neopixel[i].target = target_rgb

            print(str(count) + ': ' + recvd_color)

        # for i, _ in enumerate(neopixels):
        #     if neopixels[i].target != target_rgb:
        #         neopixels[i].target = target_rgb
        #         neopixels[i].color = neopixels[i].target
        #         neopixel_write(neopixels, neopixels[i].color, i)
        #         print("written neopixel", i, ':', neopixels[i].color)
        #         time.sleep_ms(200)

        # previous_rgb = color_transition(neopixels, previous_rgb, target_rgb)

# run the main function
if __name__ == "__main__":
    main()

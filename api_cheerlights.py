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
        self.delay = 0 # delay before changing in ms

    def write(self, color):
        ''' write to a NeoPixel '''
        self.neo.fill(color)
        self.neo.write()
        self.color = color

    def blank(self):
        ''' turn the NeoPixel off '''
        self.write((0, 0, 0))

    def new_color(self, color_name, colors):
        ''' check and convert incoming colour to RGB value and set delay before
        the colour is changed '''
        if color_name in colors:
            self.target = colors[color_name]
        else:
            self.color = colors['red'] # default to red
        self.delay = time.ticks_ms() + urandom.getrandbits(12)

    def transition(self):
        ''' check if the NeoPixel is in sync with the target and iterate to the
        target colour if not '''
        if self.color != self.target and time.ticks_ms() > self.delay:
            new = list(self.color)
            for c in range(3):
                if self.color[c] < self.target[c]:
                    new[c] += 1
                elif self.color[c] > self.target[c]:
                    new[c] -= 1
            self.write(new)

def api_request(url):
    ''' retrieve the webpage and extract field1 from the json. Contains the name
    of the Cheerlights colour '''
    feed = urequests.get(url)
    return feed.json()['field1']

def cheerlights_confirm(cheerlights, value, colors):
    if type(value) != bool:
        print("not a boolean value")
    if value == True:
        color = colors['green']
    else:
        color = colors['red']
    for i in range(3):
        # flash 3 times
        delay = 300 # ms
        for i, _ in enumerate(cheerlights):
            cheerlights[i].write(color)
        time.sleep_ms(delay)
        for i, _ in enumerate(cheerlights):
            cheerlights[i].blank()
        time.sleep_ms(delay)

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

    cheerlights   = [] # holder for the neo pixels
    pixel_pins  = [0,14,12,13,15] # D3,D5,D6,D7,D8
    num_pixels  = 1 # leds per strip

    # define pins and create neopixel objects:
    for h, _ in enumerate(pixel_pins):
        pin = Pin(pixel_pins[h], Pin.OUT)
        cheerlights.append(Cheerlight(pin, num_pixels))

    # turn off any lit neopixels:
    for i, _ in enumerate(cheerlights):
        cheerlights[i].blank()

    # seed the random generator from the analog pin
    adc = ADC(0)
    seed = adc.read()
    print("random seed: ", seed)
    urandom.seed(seed)

    # connect wifi
    wifi = Wifi()
    online = wifi.connect()
    cheerlights_confirm(cheerlights, online, colors)

    # holders for colour name
    recvd_color = ''
    prev_color = ''

    count = 0
    interval = 15 # seconds delay between updates
    last_update = -100 # time.time() + interval

    while True:
        if time.time() > last_update + interval:
            recvd_color = api_request(api)
            last_update = time.time()

            # Check if color remains the same
            if recvd_color == prev_color:
                count += 1

            # if color has changed, reset counter and update cheerlights
            else:
                count = 1
                prev_color = recvd_color

                for j, _ in enumerate(cheerlights):
                    cheerlights[j].new_color(recvd_color, colors)

            print(time.time(), ':',  count, ': ', recvd_color)

        # for k, _ in enumerate(cheerlights):
        for k in range(len(cheerlights)):
            cheerlights[k].transition()
            gc.collect()
        time.sleep_ms(25) # smooth the transition

# run the main function
if __name__ == "__main__":
    main()

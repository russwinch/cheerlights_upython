"""
Cheerlights for esp8266.

This version suppors multiple ws2812 led strips and adds the effect of them
changing at different times, replacing the original implementation with
multiple microcontrollers, but replicating the same look and feel.

Original author George Kaimakis
Modified by Russ Winch
Version: December 2018
"""

import time
import urequests
import urandom
import neopixel
from machine import Pin, ADC
from wifi import Wifi


class Cheerlight(object):
    colors = {'red': (255, 0, 0),
              'orange': (255, 30, 0),
              'yellow': (255, 110, 1),
              'green': (0, 255, 0),
              'cyan': (0, 255, 255),
              'blue': (0, 0, 255),
              'purple': (128, 0, 128),
              'magenta': (255, 0, 50),
              'pink': (255, 40, 50),
              'white': (255, 255, 170),
              'oldlace': (255, 150, 50),
              'warmwhite': (255, 150, 50),
              'off': (0, 0, 0)
              }
    target = colors['off']

    def __init__(self, pin, num_pixels):
        self.neo = neopixel.NeoPixel(pin, num_pixels)
        self.off()

    @classmethod
    def new_color(cls, color):
        try:
            cls.target = cls.colors[color]
        except KeyError:
            cls.target = cls.colors['red']

    def in_sync(self):
        return self.color == self.target

    def write(self, color):
        """Write to the NeoPixel."""
        self.neo.fill(color)
        self.neo.write()
        self.color = color

    def off(self):
        """Turn the NeoPixel off."""
        self.write(self.colors['off'])
        self.color = self.colors['off']

    def transition(self):
        """Cycle through R G B and iterate them closer to the target value."""
        delay = 25  # ms
        new = []
        for current, target in zip(self._color, self.target):
            if current < target:
                new.append(current + 1)
            elif current > target:
                new.append(current - 1)
            else:
                new.append(current)
        time.sleep_ms(delay + urandom.getrandbits(12))  # TODO: needs tuning
        self.write(new)


def api_request(url):
    """Retrieve the webpage and extract field1 from the json.

    Args:
        url (str): web page to query

    Returns:
        (str): name of the Cheerlights colour
    """
    feed = urequests.get(url)
    return feed.json()['field1']


def cheerlights_confirm(cheerlights, success):
    pulses = 3
    delay = 300  # ms
    if success:
        color = Cheerlight.colors['green']
    else:
        color = Cheerlight.colors['red']

    for i in range(pulses):
        for cheerlight in cheerlights:
            cheerlight.write(color)
        time.sleep_ms(delay)
        for cheerlight in cheerlights:
            cheerlight.off()
        time.sleep_ms(delay)


if __name__ == '__main__':
    host = 'https://thingspeak.com/'
    topic = 'channels/1417/feeds/last.json'
    api = ''.join([host, topic])

    # define pins and create neopixel objects
    pixel_pins = [0, 14, 12, 13, 15]  # D3,D5,D6,D7,D8
    # num_pixels = 4  # leds per strip
    num_pixels = 1  # low power testing
    cheerlights = []  # holder for the cheerlight objects
    for pin in pixel_pins:
        cheerlights.append(Cheerlight(Pin(pin, Pin.OUT), num_pixels))

    # turn off any lit neopixels:
    # all_cheerlights(cheerlights, 'blank')

    # seed the random generator from the analog pin
    adc = ADC(0)
    seed = 0
    for s in range(20):
        seed += adc.read()
        time.sleep_ms(10)
    print(''.join(['random seed: ', seed]))
    urandom.seed(seed)

    # connect wifi
    wifi = Wifi()
    cheerlights_confirm(cheerlights, wifi.connect())

    # holders for colour name
    recvd_color = ''
    prev_color = ''

    count = 0
    interval = 15  # seconds between updates from the api
    last_update = -1  # time.time() + interval

    while True:
        if time.time() > last_update + interval:
            received_color = api_request(api)
            last_update = time.time()

            # if color has changed, reset counter and update cheerlights
            if received_color != prev_color:
                count = 1
                prev_color = received_color
                Cheerlight.new_color(received_color)
            else:
                count += 1

            print(' : '.join([count, recvd_color]))

        for cheerlight in cheerlights:
            if not cheerlight.in_sync():
                cheerlight.transistion()

        # gc.collect() # seems to fix the intermittent 'uncallable' error
        # time.sleep_ms(25) # smooth the transition

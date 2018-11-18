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
    """A strip of ws2812 leds ready for input from cheerlights api."""
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
        """Create a cheerlight using the neopixel library and switch it off.

        Args:
            pin: (object): a machine.Pin output pin to the ws2812
            num_pixels (int): numner of leds in the strip
        """
        self.neo = neopixel.NeoPixel(pin, num_pixels)
        self.off()

    @classmethod
    def new_color(cls, color_name):
        """Set a new target color for the cheerlight to iterate towards.

        Args:
            color_name (str): the name of the color
        """
        default = 'red'
        try:
            cls.target = cls.colors[color_name]
        except KeyError:
            cls.target = cls.colors[default]

    def in_sync(self):
        """Checks if the cheerlight is in sync with the target color.

        Returns:
            (bool): True if color and target are the same
        """
        return self.color == self.target

    def write(self, color):
        """Writes a color to the neopixel.

        Args:
            color (tuple of int): rgb values of the color
        """
        self.neo.fill(color)
        self.neo.write()
        self.color = color

    def off(self):
        """Turns the cheerlight off."""
        self.write(self.colors['off'])
        self.color = self.colors['off']

    def transition(self):
        """Cycles through R G B and iterate them closer to the target value."""
        delay = 25  # ms
        new = []
        for current, target in zip(self.color, self.target):
            if current < target:
                new.append(current + 1)
            elif current > target:
                new.append(current - 1)
            else:
                new.append(current)
        time.sleep_ms(delay + urandom.getrandbits(12))  # TODO: needs tuning
        self.write(new)


def api_request(url):
    """Retrieves the web page, extracting field1 from the json.

    Args:
        url (str): web page to query

    Returns:
        (str): name of the cheerlights colour
    """
    feed = urequests.get(url)
    return feed.json()['field1']


def cheerlights_confirm(cheerlights, success):
    """Flashes all cheerlights to show success or failure.

    Args:
        cheerlights (list of obj): all cheerlights to iterate through
        success (bool): True will flash green, red for False
    """
    pulses = 3
    delay = 300  # ms
    if success:
        color = Cheerlight.colors['green']
    else:
        color = Cheerlight.colors['red']

    for _ in range(pulses):
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
    pixel_pins = [0, 14, 12, 13, 15]  # D3, D5, D6, D7, D8
    # num_pixels = 4  # leds per strip
    num_pixels = 1  # low power testing

    # holder for the cheerlight objects
    cheerlights = [Cheerlight(Pin(pin, Pin.OUT), num_pixels)
                   for pin in pixel_pins]

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

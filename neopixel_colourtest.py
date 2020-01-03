"""
Neopixel colour tester.
To help with the tuning of cheerlights colour
names to your brand of Neopixel / WS2182 leds

@authors George Kaimakis and Russ Winch
@version 30 Nov 2017
"""

import time
import machine
import neopixel

# Global variables:
# PIXEL_PIN           = 12
# NUM_OF_PIXELS       = 1

# look-up color dict - cheerlights api 'field1' is used as the key:
"""
colors = {
    'red':      (255,0,0),
    'orange':   (211,84,0),
    'yellow':   (254,183,12),
    'green':    (0,200,0),
    'cyan':     (0,255,255),
    'blue':     (0,0,255),
    'purple':   (100,0,160),
    'magenta':  (255,0,255),
    'pink':     (254,52,62),
    'white':    (255,255,170),
    'oldlace':  (255,200,130),
    'warmwhite':(255,200,130),
    }
"""

# define pin and create neopixel object:
# pin = machine.Pin(PIXEL_PIN, machine.Pin.OUT)
# np = neopixel.NeoPixel(pin, NUM_OF_PIXELS)

def new_neopixel_color(neo, next_color):
    neo.fill(next_color)
    neo.write()

def neopixel_write(neo, color, *args):
    if len(args) == 1:
        i = args[0]
        neo[i].fill(color)
        neo[i].write()
    # ignore none or too many arguments
    else:
        # for i in range(len(neo)):
            # neo[i].fill(color)
            # neo[i].write()
        neo.fill(color)
        neo.write()

def neopixel_blank(np):
    # for i, _ in enumerate(np):
    np.fill((0,0,0))
    np.write()

def to_int(string):
    integer = []
    for i in string:
        integer.append(int(i))
    return integer

def get_rgb(color):
    color = color.split(' ')

    if len(color) == 1:
        try:
            rgb = colors[color[0]]
            print(rgb)
            return rgb
        except:
            print("Not a cheerlights colour")
            return False

    elif len(color) == 3:
        try:
            return to_int(color)
        except:
            print("Invalid RGB values")
            return False

    else:
        print('Invalid entry. Enter a colour name or RGB values')
        return False

def color_transition(neo, previous, target):
    """compares previous and target rgb values & calculates the transition.
    writes to the neopixel & returns the new color value to the caller to be
    asigned as the next previous_rgb value.
    """
    speed = 10 # ms delay after each transition
    new = list(previous)
    print(previous)
    while target != new:
        # if previous != target:
        for i, _ in enumerate(previous):
            for j, val in enumerate(previous[i])
                if previous[i][val] < target[i][val]:
                new[i][val] += 1
                elif previous[i][val] > target[i][val]:
                new[i][val] -= 1
        neopixel_write(neo, new)
        time.sleep_ms(speed) # smooth the transition
        # if previous == target:
        #     return tuple(new)
    print(target)
    return tuple(new)


def main():

    colors = {
        'red':      (255,0,0),
        'orange':   (211,84,0),
        'yellow':   (254,183,12),
        'green':    (0,200,0),
        'cyan':     (0,255,255),
        'blue':     (0,0,255),
        'purple':   (100,0,160),
        'magenta':  (255,0,255),
        'pink':     (254,52,62),
        'white':    (255,255,170),
        'oldlace':  (255,200,130),
        'warmwhite':(255,200,130),
        }

    # neopixels   = [] # holder for the neo pixels
    pixel_pin  = 12 # D3
    num_pixels  = 1 # leds per strip

    previous_rgb = (0, 0, 0)
    target_rgb = (0, 0, 0)

    # define pins, create neopixel objects, and populate neopixels list:
    # for i in range(len(pixel_pins)):
    pin = machine.Pin(pixel_pin, machine.Pin.OUT)
    np = neopixel.NeoPixel(pin, num_pixels)

    # turn off any lit neopixels:
    neopixel_blank(np)

    # request user input - color in either name or RGB value:
    print(pixel_pin)
    print(num_pixels)
    print(previous_rgb)
    print(target_rgb)
    print(pin)
    print(np)
    print("Enter a cheerlights colour name or RGB values separated with a space")

    while True:
        color = input('Colour > ')
        target_rgb = get_rgb(color)

        # update color:
        if target_rgb != False and target_rgb != previous_rgb:
            # new_neopixel_color(new_rgb)
            print(previous_rgb, target_rgb)
            next_color = color_transition(np, previous_rgb, target_rgb)
            # next_color = new_neopixel_color(np, target_rgb)

            previous_rgb = next_color

# run the main function
if __name__ == "__main__":
    main()

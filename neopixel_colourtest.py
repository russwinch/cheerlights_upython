'''
Neopixel colour tester. 
To help with the tuning of cheerlights colour 
names to your brand of Neopixel / WS2182 leds

@author George Kaimakis and Russ Winch
@version 30 Nov 2017
'''

import neopixel
import machine

# Global variables:
PIXEL_PIN           = 0
NUM_OF_PIXELS       = 4

# look-up color dict - cheerlights api 'field1' is used as the key:
colors = {
    'red':(255,0,0),
    'orange':(255,30,0),
    'yellow':(254,183,12),
    'green':(0,128,0),
    'cyan':(0,255,255),
    'blue':(0,0,255),
    'purple':(128,0,128),
    'magenta':(255,0,255),
    'pink':(254,52,62),
    'white':(255,255,230),
    'oldlace':(255,200,130),
    'warmwhite':(255,200,130)
    }

# define pin and create neopixel object:
pin = machine.Pin(PIXEL_PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_OF_PIXELS)

def new_neopixel_color(next_color):
    np.fill(next_color)
    np.write()

def neopixel_blank():
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

# turn off any lit neopixels:
neopixel_blank()

print("Enter a cheerlights colour name or RGB vales separated by space")

while True:
    color = input('Colour > ')
    rgb = get_rgb(color)

    # update colour
    if rgb != False:
        new_neopixel_color(rgb)

print("Clearing Cached Variables...", end="")
for name in dir():
    if not name.startswith('_'):
        del globals()[name]
print(" Done\n")
import gc
print("gc.mem_free() before import :\t" + str(gc.mem_free()))
import KPU as kpu
from Maix import utils
print("gc.mem_free() after import:\t" + str(gc.mem_free()))
utils.gc_heap_size(0xAF000)
print("utils.gc_heap_size():\t" + str(utils.gc_heap_size()))

################# Done Init #################

import lcd
import image
from fpioa_manager import *
from Maix import FPIOA, GPIO
from cocorobo import display_cjk_string

_buttonLeft, _buttonRight = 9, 10

fpiol, fpior = FPIOA(), FPIOA()

fpiol.set_function(_buttonLeft,FPIOA.GPIO0)
fpior.set_function(_buttonRight,FPIOA.GPIO1)

_key_gpio_left=GPIO(GPIO.GPIO0,GPIO.IN)
_key_gpio_right=GPIO(GPIO.GPIO1,GPIO.IN)

import time

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
image = image.Image("/sd/preset/images/splash_cocorobo.jpg")
lcd.display(image, oft=(0, 0))

display_cjk_string(image, 0, 0, "Press Button A&B to Resize", font_size=1, color=(255,255,255))
lcd.display(image, oft=(0, 0))

while True:
    
    if _key_gpio_left.value() == 1:
        lcd.clear(lcd.BLACK)
        final_display = image.resize(120, 120)
        lcd.display(final_display, oft=(0, 0))
        del final_display
        time.sleep_ms(200)
    elif _key_gpio_right.value() == 1:
        lcd.clear(lcd.BLACK)
        final_display = image.resize(240, 240)
        lcd.display(final_display, oft=(0, 0))
        del final_display
        time.sleep_ms(200)

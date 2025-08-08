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

import math

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
canvas = image.Image("/sd/preset/images/splash_bg.jpg")
radius = 80
initial_degree = 0
canvas.draw_rectangle(0,0, 240, 240, color=(0,0,0), thickness=1, fill=True)

while True:
    if _key_gpio_right.value() == 1:
        initial_degree = initial_degree - 1
    elif _key_gpio_left.value() == 1:
        initial_degree = initial_degree + 1
    if initial_degree > 359:
        initial_degree = 0
    if initial_degree < 0:
        initial_degree = 359
    print(initial_degree)
    canvas.draw_arrow(120,120,(int((120 + radius * math.sin(math.radians((initial_degree - 1)))))),(int((120 + radius * math.cos(math.radians((initial_degree - 1)))))), color=(0, 0, 0), thickness=2)
    canvas.draw_arrow(120,120,(int((120 + radius * math.sin(math.radians((initial_degree + 1)))))),(int((120 + radius * math.cos(math.radians((initial_degree + 1)))))), color=(0, 0, 0), thickness=2)
    canvas.draw_arrow(120,120,(int((120 + radius * math.sin(math.radians(initial_degree))))),(int((120 + radius * math.cos(math.radians(initial_degree))))), color=(255, 0, 0), thickness=2)
    canvas.draw_rectangle(8,8, 100, 20, color=(0,0,0), thickness=1, fill=True)

    display_cjk_string(canvas, 8, 8, (str(initial_degree) + str(" deg")), font_size=1, color=(255,0,0))
    lcd.display(canvas, oft=(0, 0))

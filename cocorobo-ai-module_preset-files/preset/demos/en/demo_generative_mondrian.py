import lcd
import image
from fpioa_manager import *
from Maix import FPIOA, GPIO

_buttonLeft, _buttonRight = 9, 10

fpiol, fpior = FPIOA(), FPIOA()

fpiol.set_function(_buttonLeft,FPIOA.GPIO0)
fpior.set_function(_buttonRight,FPIOA.GPIO1)

_key_gpio_left=GPIO(GPIO.GPIO0,GPIO.IN)
_key_gpio_right=GPIO(GPIO.GPIO1,GPIO.IN)

import random
import math

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)

canvas = image.Image(size=(240, 240))

red = (255, 0, 0)
white = (240, 240, 240240)
blue = (0, 0, 255)
black = (0, 0, 0)
yellow = (255, 255, 0)

colors = (white, yellow, red, blue)
initial_w = 40
initial_h = 90
button_state_a = False
button_state_b = False
a = colors[0]
b = colors[2]
c = colors[0]
d = colors[3]
e = colors[0]
f = colors[0]
g = colors[2]

def generative_mondrian():
	global a, b, black, blue, button_state_a, button_state_b, c, canvas, colors, d, e, f, g, initial_h, initial_w, red, white, yellow
	canvas.draw_rectangle(0,0, initial_w, initial_h, color=a, thickness=1, fill=True)
	canvas.draw_rectangle(0,initial_h, initial_w, 10, color=black, thickness=1, fill=True)
	canvas.draw_rectangle(((initial_w + 10) + math.floor((240 - (10 + initial_w)) * 0.6)),(((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10), 10, (240 - (((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10)), color=black, thickness=1, fill=True)
	canvas.draw_rectangle(initial_w,0, 10, 240, color=black, thickness=1, fill=True)
	canvas.draw_rectangle(0,((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)), 240, 10, color=black, thickness=1, fill=True)
	canvas.draw_rectangle((initial_w + 10),0, (240 - (10 + initial_w)), (math.floor(initial_h * 1.8)), color=b, thickness=1, fill=True)
	canvas.draw_rectangle(0,(initial_h + 10), initial_w, (math.floor((initial_h * 1.8 - 10) - initial_h)), color=c, thickness=1, fill=True)
	canvas.draw_rectangle(0,(((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10), initial_w, (240 - (((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10)), color=d, thickness=1, fill=True)
	canvas.draw_rectangle((initial_w + 10),(((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10), (math.floor((240 - (10 + initial_w)) * 0.6)), (240 - (((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10)), color=e, thickness=1, fill=True)
	canvas.draw_rectangle((((initial_w + 10) + math.floor((240 - (10 + initial_w)) * 0.6)) + 10),(((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10), (240 - (((initial_w + 10) + math.floor((240 - (10 + initial_w)) * 0.6)) + 10)), (math.floor((240 - (((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10)) / 2 - 10)), color=f, thickness=1, fill=True)
	canvas.draw_rectangle((((initial_w + 10) + math.floor((240 - (10 + initial_w)) * 0.6)) + 10),((((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10) + math.floor((240 - (((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10)) / 2 - 10)), (240 - (((initial_w + 10) + math.floor((240 - (10 + initial_w)) * 0.6)) + 10)), 10, color=black, thickness=1, fill=True)
	canvas.draw_rectangle((((initial_w + 10) + math.floor((240 - (10 + initial_w)) * 0.6)) + 10),(((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + (math.floor((240 - (((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10)) / 2 - 10) + 20)), (240 - (((initial_w + 10) + math.floor((240 - (10 + initial_w)) * 0.6)) + 10)), ((((240 - math.floor(initial_h * 1.8)) - 10) - math.floor((240 - (((initial_h + 10) + math.floor((initial_h * 1.8 - 10) - initial_h)) + 10)) / 2 - 10)) - 10), color=g, thickness=1, fill=True)
	_canvas_x, _canvas_y = 0, 0
	lcd.display(canvas, oft=(_canvas_x,_canvas_y))


generative_mondrian()

while True:
	if (_key_gpio_left.value() == 0) and button_state_a == False:
		initial_w = random.randint(10, 200)
		a = colors[random.randint(0, 3)]
		b = colors[random.randint(0, 3)]
		c = colors[random.randint(0, 3)]
		d = colors[random.randint(0, 3)]
		e = colors[random.randint(0, 3)]
		f = colors[random.randint(0, 3)]
		g = colors[random.randint(0, 3)]
		generative_mondrian()
		button_state_a = True
	elif (_key_gpio_left.value() == 1) and button_state_a == True:
		button_state_a = False
	if (_key_gpio_right.value() == 0) and button_state_b == False:
		initial_h = random.randint(10, 100)
		a = colors[random.randint(0, 3)]
		b = colors[random.randint(0, 3)]
		c = colors[random.randint(0, 3)]
		d = colors[random.randint(0, 3)]
		e = colors[random.randint(0, 3)]
		f = colors[random.randint(0, 3)]
		g = colors[random.randint(0, 3)]
		generative_mondrian()
		button_state_b = True
	elif (_key_gpio_right.value() == 1) and button_state_b == True:
		button_state_b = False

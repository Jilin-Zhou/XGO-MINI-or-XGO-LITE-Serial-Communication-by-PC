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



lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
button_a_state = False
button_b_state = False

img = image.Image(size=(240, 240))

display_cjk_string(img, 0, 0, "Press any button", font_size=1, color=(255,255,255))
display_cjk_string(img, 0, 20, "to change color", font_size=1, color=(255,255,255))
lcd.display(img,oft=(0,0))


while True:
    if (_key_gpio_left.value() == 1) and button_a_state == False:
        print("A pressed.")
        lcd.clear(lcd.RED)
        button_a_state = True
    elif (_key_gpio_left.value() == 0) and button_a_state == True:
        button_a_state = False
    if (_key_gpio_right.value() == 1) and button_b_state == False:
        print("B pressed.")
        lcd.clear(lcd.BLUE)
        button_b_state = True
    elif (_key_gpio_right.value() == 0) and button_b_state == True:
        button_b_state = False

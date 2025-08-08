import lcd
import image
import time
from cocorobo import display_cjk_string

img = image.Image(size=(240, 240))

def textdraw(x):
    global canvas, initial_degree, radius, button_b_state, button_a_state, i
    img.clear()
    img.draw_rectangle(0,0,240,240,fill=True,color=(255,0,0))
    display_cjk_string(img, 0, 0, (str(str(x)) + str("度")), font_size=1, color=(255,255,255))
    display_cjk_string(img, 150, 0, (str(str(x)) + str("度")), font_size=1, color=(255,255,255))
    display_cjk_string(img, 0, 220, (str(str(x)) + str("度")), font_size=1, color=(255,255,255))
    display_cjk_string(img, 150, 220, (str(str(x)) + str("度")), font_size=1, color=(255,255,255))
    lcd.display(img,oft=(0,0))

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)

while True:
    lcd.clear((0,0,0))
    lcd.rotation(1)
    textdraw(0)
    time.sleep_ms(1000)
    lcd.clear((0,0,0))
    lcd.rotation(2)
    textdraw(90)
    time.sleep_ms(1000)
    lcd.clear((0,0,0))
    lcd.rotation(3)
    textdraw(180)
    time.sleep_ms(1000)
    lcd.clear((0,0,0))
    lcd.rotation(0)
    textdraw(270)
    time.sleep_ms(1000)

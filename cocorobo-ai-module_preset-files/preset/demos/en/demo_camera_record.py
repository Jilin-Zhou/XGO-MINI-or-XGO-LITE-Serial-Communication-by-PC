import lcd
import image
import sensor
import time
from fpioa_manager import *
from Maix import FPIOA, GPIO

_buttonLeft, _buttonRight = 9, 10

fpiol, fpior = FPIOA(), FPIOA()

fpiol.set_function(_buttonLeft,FPIOA.GPIO0)
fpior.set_function(_buttonRight,FPIOA.GPIO1)

_key_gpio_left=GPIO(GPIO.GPIO0,GPIO.IN)
_key_gpio_right=GPIO(GPIO.GPIO1,GPIO.IN)

import video
from Maix import GPIO

_record_vid = None

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.skip_frames(30)
sensor.run(1)
sensor.set_windowing((224,224))
sensor.set_auto_exposure(False)
img = image.Image(size=(240, 240))

button_a_state = 0
button_b_state = 0
record_state = 0

try:from cocorobo import display_cjk_string
except:pass

def lcd_draw_string(canvas, x, y, text, color=(255,255,255), font_size=1, scale=1, mono_space=False, auto_wrap=True):
    try: display_cjk_string(canvas, x, y, text, font_size=font_size, color=color)
    except: canvas.draw_string(x, y, text, color=color, scale=scale, mono_space=mono_space)

def record():
    global _record_vid
    _record_vid = video.open("/sd/user/record.avi", record=1, width=224, height=224, interval=20000, quality=80)

button_count = 0

while True:
    camera = sensor.snapshot()
    camera.draw_rectangle(0,0,224,50,color=(0,0,0),fill=True)
    lcd_draw_string(camera, 5,0, "Press Button A or B to", color=(255,255,255), scale=1, mono_space=False)
    lcd_draw_string(camera, 5,25, "Start & Stop Record", color=(255,255,255), scale=1, mono_space=False)
    lcd.display(camera, oft=(8, 8))

    if (_key_gpio_left.value() == 1) and button_a_state == 0:
        record()

        record_state = 1
        button_count += 1
        if button_count > 1: button_count =0
        print(button_count)

        button_a_state = 1
    elif (_key_gpio_left.value() == 0) and button_a_state == 1:
        button_a_state = 0

    if (_key_gpio_right.value() == 1) and button_b_state == 0:
        record()

        record_state = 1
        button_count += 1
        if button_count > 1: button_count =0
        print(button_count)

        button_b_state = 1
    elif (_key_gpio_right.value() == 0) and button_b_state == 1:
        button_b_state = 0


    while button_count == True:
        print("Recording, " + str(button_count))

        camera = sensor.snapshot()
        camera.draw_rectangle(0,0,224,20,fill=True,color=(255,0,0))
        display_cjk_string(camera, 0,0, "Recoding video...", font_size=1, color=(255,255,255))
        lcd.display(camera, oft=(8, 8))

        _record_vid.record(camera)

        if (_key_gpio_left.value() == 1) and button_a_state == 0:
            # record()

            record_state = 1
            button_count += 1
            if button_count > 1: button_count =0
            print(button_count)

            button_a_state = 1
        elif (_key_gpio_left.value() == 0) and button_a_state == 1:
            button_a_state = 0

        if (_key_gpio_right.value() == 1) and button_b_state == 0:
            # record()

            record_state = 1
            button_count += 1
            if button_count > 1: button_count =0
            print(button_count)

            button_b_state = 1
        elif (_key_gpio_right.value() == 0) and button_b_state == 1:
            button_b_state = 0

        if button_count == False: 
            camera.draw_rectangle(0,0,224,20,fill=True,color=(0,0,0))
            display_cjk_string(camera, 0,0, "Recording finished.", font_size=1, color=(255,255,255))
            lcd.display(camera, oft=(8, 8))
            _record_vid.record_finish()
            time.sleep(1)
            camera.clear()
            break

    '''
    if button_count == 1:
        camera.draw_rectangle(0,0,224,20,fill=True,color=(255,0,0))
        display_cjk_string(camera, 0,0, "Recoding video...", font_size=1, color=(255,255,255))
        lcd.display(camera, oft=(8, 8))

        _record_vid.record(camera)
    if button_count == 0:
        camera.draw_rectangle(0,0,224,20,fill=True,color=(0,0,0))
        display_cjk_string(camera, 0,0, "Recoding finished.", font_size=1, color=(255,255,255))
        lcd.display(camera, oft=(8, 8))
        _record_vid.record_finish()
    '''


print("Clearing Cached Variables...", end="")
for name in dir(): 
    if not name.startswith('_'): 
        del globals()[name]
print(" Done")
import KPU as kpu
kpu.memtest()
from Maix import utils
utils.gc_heap_size()

################# Done Init #################

import time

import lcd
import image
import os, json, time, utime, struct
from Maix import I2S, GPIO
from modules import SpeechRecognizer
from fpioa_manager import *
fm.register(31, fm.fpioa.GPIO3)
fm.register(32, fm.fpioa.GPIO4)
from cocorobo import display_cjk_string

_led_red = GPIO(GPIO.GPIO3, GPIO.OUT)
_led_blue = GPIO(GPIO.GPIO4, GPIO.OUT)

def _sr_data_save(s,content,keyword_num, model_num, path):
    data = _s_daemon.get_model_data(keyword_num, model_num)
    with open(path,'w') as f:
        f.write(data)

def _sr_data_load(s, keyword_num, model_num,frame_num, path):
    print(path)
    with open(path,'r') as f:
        data = f.read()
        _s_daemon.add_voice_model(keyword_num, model_num, frame_num, data)

def _sr_init_remove_old_recording():
    global _voice_record
    try:
        for i in os.listdir("/sd/sr"):
            print("deleting " + str(i) + "...")
            os.remove("/sd/sr/"+str(i))
        print("file deleting done.")
        os.rmdir("/sd/sr")
        print("directory deleting done.")
        os.mkdir("/sd/sr")
        print("directory creating done.")
    except:
        os.mkdir("/sd/sr")
        print("directory creating done.")
    _voice_record = True

# Enable Microphone and Disable Wifi Feature
fm.register(20, fm.fpioa.I2S0_IN_D0, force=True)
fm.register(18, fm.fpioa.I2S0_SCLK, force=True)
fm.register(19, fm.fpioa.I2S0_WS, force=True)
fm.register(8, fm.fpioa.GPIO5, force=True)
wifi_en=GPIO(GPIO.GPIO5,GPIO.OUT)
wifi_en.value(0)

# Init recording device parameteres
sample_rate = 8000
i2s_dev = I2S(I2S.DEVICE_0)
# config i2s according to speechrecognizer
i2s_dev.channel_config(i2s_dev.CHANNEL_0,I2S.RECEIVER,resolution = I2S.RESOLUTION_16_BIT,cycles = I2S.SCLK_CYCLES_32,align_mode = I2S.STANDARD_MODE)
i2s_dev.set_sample_rate(sample_rate)
_s_daemon = SpeechRecognizer(i2s_dev)
_s_daemon.set_threshold(0,0,20000)

from fpioa_manager import *
from Maix import FPIOA, GPIO

_gp_side_buttons = [9, 10, 11]

FPIOA().set_function(_gp_side_buttons[0],FPIOA.GPIO0)
FPIOA().set_function(_gp_side_buttons[1],FPIOA.GPIO1)
FPIOA().set_function(_gp_side_buttons[2],FPIOA.GPIO2)

_gp_side_a = GPIO(GPIO.GPIO0,GPIO.IN,GPIO.PULL_UP)
_gp_side_b = GPIO(GPIO.GPIO1,GPIO.IN,GPIO.PULL_UP)
_gp_side_c = GPIO(GPIO.GPIO2,GPIO.IN,GPIO.PULL_UP)

import time

_voice_recording_load = True
_voice_recording_ready = False

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
canvas = image.Image(size=(240, 240))

_canvas_x, _canvas_y = 0, 0

try:
    if _voice_recording_load == True:
        _sr_filelist = os.listdir("/sd/sr")
        for _sr_file in _sr_filelist:
            _sr_frm_num = int(_sr_file[4:_sr_file.find(".")])
            print(_sr_frm_num)
            print("/sd/sr/" + str(_sr_file))
            _sr_data_load(_s_daemon, int(_sr_file[0]), int(_sr_file[2]), _sr_frm_num, "/sd/sr/" + str(_sr_file))
        print("load successful!")
except BaseException as e:
    canvas.clear()

    display_cjk_string(canvas, 3,0, "加载错误", color=(255,0,0), font_size=2)
    display_cjk_string(canvas, 3,110, "此识别演示将", color=(160,160,160), font_size=1)
    display_cjk_string(canvas, 3,130, "识别3个不同的剪辑,", color=(160,160,160), font_size=1)
    display_cjk_string(canvas, 3,150, "但您必须记录样本", color=(160,160,160), font_size=1)
    display_cjk_string(canvas, 3,170, "通过使用该程序", color=(160,160,160), font_size=1)
    display_cjk_string(canvas, 3,190, "首先从演示菜单:", color=(160,160,160), font_size=1)
    display_cjk_string(canvas, 3,210, "语音识别（记录）", color=(0,220,220), font_size=1)

    lcd.display(canvas, oft=(_canvas_x,_canvas_y))
    print("load error")
    time.sleep(4)
    import machine
    machine.reset()

first_time = 0

while True:
    canvas.clear()


    display_cjk_string(canvas, 3,0, "按下按钮A", color=(255,255,255), font_size=1)
    display_cjk_string(canvas, 3,25, "开始识别", color=(255,255,255), font_size=1)

    lcd.display(canvas, oft=(_canvas_x,_canvas_y))

    if _gp_side_a.value() == 1:
        _s_recognition_state = 0
        _s_daemon.recognize()
        time.sleep_ms(500)

        canvas.clear()

        display_cjk_string(canvas, 3, 0, "现在开始说！", color=(0,255,0), font_size=1)
        
        lcd.display(canvas, oft=(_canvas_x,_canvas_y))
        while _s_recognition_state == 0:
            if (_s_daemon.get_status() == 5):
                print("", end="")
            elif (_s_daemon.get_status() == 3):
                print("", end="")
            elif (_s_daemon.get_status() == 4):
                print("[CocoRobo] Record OK, Proceed!")
                _s_recognition_state = 1
            else:
                print("[CocoRobo] Current state: " + str(s.get_status()))

        time.sleep_ms(800)
        _s_ret = _s_daemon.get_result()
        print("[CocoRobo] Result: " + str(_s_ret))

        if (_s_ret > 0):
            if (_s_ret == 1):
                canvas.clear()
                canvas.draw_rectangle(0,0, 240, 240, color=(255,0,0), thickness=1, fill=True)
                lcd.display(canvas, oft=(_canvas_x,_canvas_y))
                time.sleep_ms(1000)
            elif (_s_ret == 2):
                canvas.clear()
                canvas.draw_rectangle(0,0, 240, 240, color=(51,255,51), thickness=1, fill=True)
                lcd.display(canvas, oft=(_canvas_x,_canvas_y))
                time.sleep_ms(1000)
            elif (_s_ret == 3):
                canvas.clear()
                canvas.draw_rectangle(0,0, 240, 240, color=(51,51,255), thickness=1, fill=True)
                lcd.display(canvas, oft=(_canvas_x,_canvas_y))
                time.sleep_ms(1000)
        else: 
            canvas.clear()
            canvas.draw_rectangle(0,0, 240, 240, color=(0,0,0), thickness=1, fill=True)


            display_cjk_string(canvas, 3,0, "没有", color=(255,0,0), font_size=1)
            display_cjk_string(canvas, 3,25, "已识别", color=(255,0,0), font_size=1)

            lcd.display(canvas, oft=(_canvas_x,_canvas_y))
            time.sleep_ms(1000)


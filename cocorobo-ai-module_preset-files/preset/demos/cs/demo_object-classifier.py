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

import sensor
import lcd
from Maix import FPIOA, GPIO
import time
import gc
from cocorobo import display_cjk_string

def draw_string(img, x, y, text, color, scale, bg=None ):
    if bg:
        img.draw_rectangle(x-2,y-2, len(text)*10*scale+4 , 24*scale, fill=True, color=bg)
    img = img.draw_string(x, y, text, color=color,scale=scale*2,mono_space=False)
    return img

class_names = ["1", "2", "3"]
class_num = len(class_names)
sample_num = len(class_names) * 5
THRESHOLD = 11
board_cube = 0
button_state = False

lcd.init(type=2)
lcd.rotation(1)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.run(1)

FPIOA().set_function(10, FPIOA.GPIO1)
key1 = GPIO(GPIO.GPIO1,GPIO.IN,GPIO.PULL_UP)

try:
    del model
except Exception:
    pass
try:
    del classifier
except Exception:
    pass
gc.collect()


print("===")
model_file_name = ""
import os
for i in os.listdir("/sd/preset/models"):
    name = str(i)
    if name[0] != "." and "object_classifier" in name:
        print(name)
        model_file_name = name
print("===")

#model = kpu.load(0x300000)
kpu.memtest()
model = kpu.load("/sd/preset/models/" + str(model_file_name))
classifier = kpu.classifier(model, class_num, sample_num)
kpu.memtest()

cap_num = 0
train_status = 0
last_cap_time = 0
last_btn_status = 0
res_index = -1



while True:
    img = sensor.snapshot()
    kpu.memtest()
    if board_cube:
        img = img.rotation_corr(z_rotation=90)
        img.pix_to_ai()
    # capture img
    if train_status == 0:
        if key1.value() == 0 and last_btn_status == 1:
            #time.sleep_ms(30)
            #if key1.value() == 1 and (last_btn_status == 1) and (time.ticks_ms() - last_cap_time > 500):
            last_btn_status = 0
            last_cap_time = time.ticks_ms()
            if cap_num < class_num:
                index = classifier.add_class_img(img)
                cap_num += 1
                print("add class img:", index)
            elif cap_num < class_num + sample_num:
                index = classifier.add_sample_img(img)
                cap_num += 1
                print("add sample img:", index)
            #else:
            #    img = draw_string(img, 2, 200, "release boot key please", color=lcd.WHITE,scale=1, bg=lcd.RED)
        else:
            #time.sleep_ms(30)
            if key1.value() == 1 and (last_btn_status == 0):
                last_btn_status = 1
            if cap_num < class_num:
                img.draw_rectangle(0, 0, 240,20, fill=True, color=(0,0,0))
                display_cjk_string(img, 0, 0, "按右键拍摄"+class_names[cap_num], font_size=1, color=(255,255,255))
                # img = draw_string(img, 0, 2, "press right key to cap "+class_names[cap_num], color=lcd.WHITE,scale=1, bg=lcd.RED)
            elif cap_num < class_num + sample_num:
                img.draw_rectangle(0, 0, 240,20, fill=True, color=(0,0,0))
                display_cjk_string(img, 0, 0, "按右键采集样本"+ str(cap_num-class_num), font_size=1, color=(255,255,255))
                # img = draw_string(img, 0, 2, "right key to cap sample{}".format(cap_num-class_num), color=lcd.WHITE,scale=1, bg=lcd.RED)
    # train and predict
    if train_status == 0:
        if cap_num >= class_num + sample_num:
            print("start train")
            img.draw_rectangle(0,0, 240,20, fill=True, color=(0,0,0))
            display_cjk_string(img, 0, 0, "正在识别样本中...", font_size=1, color=(255,255,255))
            # img = draw_string(img, 30, 100, "training...", color=lcd.WHITE,scale=1, bg=lcd.RED)
            lcd.display(img)
            classifier.train()
            print("train end")
            train_status = 1
    else:
        res_index = -1
        try:
            res_index, min_dist = classifier.predict(img)
            print("{:.2f}".format(min_dist))
        except Exception as e:
            print("predict err:", e)
        if res_index >= 0 and min_dist < THRESHOLD :
            print("predict result:", class_names[res_index])
            img.draw_rectangle(0,0, 240,20, fill=True, color=(0,0,0))
            display_cjk_string(img, 0, 2, class_names[res_index], font_size=1, color=(255,255,255))
            # img = draw_string(img, 2, 2, class_names[res_index], color=lcd.WHITE,scale=1, bg=lcd.RED)
        else:
            print("unknown, maybe:", class_names[res_index])
            img.draw_rectangle(0,0, 240,20, fill=True, color=(0,0,0))
            display_cjk_string(img, 0, 2, '样本可能是'+ class_names[res_index], font_size=1, color=(255,255,255))
    img = img.cut(0,0,240,240)
    lcd.display(img, oft=(0,0))
    if "1" == (class_names[res_index] if res_index != -1 else ""):
        print("Object 1")
    elif "2" == (class_names[res_index] if res_index != -1 else ""):
        print("Object 2")
    elif "3" == (class_names[res_index] if res_index != -1 else ""):
        print("Object 3")

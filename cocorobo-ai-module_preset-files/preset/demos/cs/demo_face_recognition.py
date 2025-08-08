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

import os, Maix, lcd, image, sensor, gc, time
from cocorobo import display_cjk_string

gc.enable()

lcd.init(type=2,freq=15000000,width=240,height=240,color=(255,255,255))
lcd.rotation(1)
lcd.clear(0,0,0)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.run(1)

gc.collect()
task = kpu.load("/sd/preset/models/preset/face-recognition.kmodel")
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
gc.collect()

while(True):
    gc.collect()

    img_raw = sensor.snapshot()
    code = kpu.run_yolo2(task, img_raw)

    img = img_raw.resize(224,168)
    a = img.ai_to_pix()

    a = img.draw_circle(112, 84, 1, fill=True)

    if code:
        for i in code:
            coordinate = str(i.x()) + "," + str(i.y()) + "," + str(i.w()) + "," + str(i.h()) 

            a = img.draw_rectangle(int(i.x()/1.42),int(i.y()/1.42),int(i.w()/1.42),int(i.h()/1.42), thickness=(2))
            face_count = int(i.objnum())
            print(i)
    else:
        face_count = 0

    img.draw_rectangle(0,0,224,20,fill=True,color=(0,0,0))
    # img.draw_rectangle(0,160,224,20,fill=True,color=(0,0,0))

    display_cjk_string(img, 0, 0, "人脸识别演示", font_size=1, color=(255,255,255))
    display_cjk_string(img, 0, 150, "脸的数量: " + str(face_count), font_size=1, color=(255,255,255))

    lcd.display(img, oft=(8,38))

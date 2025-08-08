import sensor,image,lcd, time, gc
import KPU as kpu
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

task = kpu.load("/sd/preset/models/cocorobo.kmodel")
anchor = (0.738768, 0.874946, 2.42204, 2.65704, 4.30971, 7.04493, 10.246, 4.59428, 12.6868, 11.8741)
a = kpu.init_yolo2(task, 0.6, 0.3, 5, anchor)

xAlign = 0
yAlign = 0
wFrame = 0
hFrame = 0
iConfidence = 0
iObjnum = 0

while(True):
    try:
        gc.collect()

        img_raw = sensor.snapshot()
        code = kpu.run_yolo2(task, img_raw)

        img = img_raw.resize(224,168)
        a = img.ai_to_pix()

        if code:
            for i in code:
                coordinate = str(i.x()) + "," + str(i.y()) + "," + str(i.w()) + "," + str(i.h()) 

                print(i)

                xAlign = int(int(i.x()/1.42)+int((i.w()/1.42)/2)-120)
                yAlign = int(int(i.y()/1.42)+int((int(i.h()/1.42)/2))-90)
                wFrame = int(i.w()/1.42)
                hFrame = int(i.h()/1.42)
                iConfidence = int(i.value()*100)
                iObjnum = int(i.objnum())

                a = img.draw_rectangle(int(i.x()/1.42),int(i.y()/1.42),int(i.w()/1.42),int(i.h()/1.42), thickness=(2))
                display_cjk_string(img, int(i.x()/1.42), int(i.y()/1.42)-24, "置信度:" + str(int(i.value()*100)) + "%", font_size=1, color=(255,255,255))
                img.draw_circle(int(i.x()/1.42)+int((i.w()/1.42)/2), int(i.y()/1.42)+int((int(i.h()/1.42)/2)), 2,color=(255,255,255),fill=True)
        else:
            iObjnum = 0
            iConfidence = '0'

        a = lcd.display(img, oft=(8,38))
        # lcd.draw_string(8, 8,"CocoRobo Logo Finder", lcd.WHITE)
        # lcd.draw_string(8, 218, str(iConfidence)+"%"+", Number of targets: "+str(iObjnum), lcd.WHITE, lcd.BLACK)
    except BaseException as e:
        print("something went wrong: " + str(e))
        # machine.reset()

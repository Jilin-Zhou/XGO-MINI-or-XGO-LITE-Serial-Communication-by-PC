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

import lcd
import image
import sensor
from cocorobo import display_cjk_string

task_customized_model = kpu.load("/sd/user/hktrashclassification_9classes.kmodel")
anchor_customized_model = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
a = kpu.init_yolo2(task_customized_model, 0.6, 0.3, 5, anchor_customized_model)

classes_customized_model = ["book", "plasticcomb", "paperbag", "newspaper", "ziptopcan", "clip", "dryingrack", "garbagecan", "lighter"]

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

while True:
    camera = sensor.snapshot()
    code_customized_model = kpu.run_yolo2(task_customized_model, camera)
    if code_customized_model:
        for i in (code_customized_model):
            camera.draw_rectangle((i.x()),(i.y()), (i.w()), (i.h()), color=(51,102,255), thickness=2, fill=False)
            camera.draw_rectangle((i.x()),(i.y()), (i.w()), 25, color=(51,102,255), thickness=2, fill=True)
            display_cjk_string(camera, ((i.x()) + 5),((i.y()) + 5), (str(classes_customized_model[i.classid()])), font_size=1, color=(255,255,255))
    lcd.display(camera, oft=(8, 8))

import sensor
import image
import lcd
import time
import gc
from cocorobo import display_cjk_string

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(0,0,0)

gc.enable()
gc.collect()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224,224))
sensor.set_colorbar(False)
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.set_auto_whitebal(False)
sensor.run(1)
sensor.skip_frames()

fcr_threshold_red = (30, 100, 15, 127, 15, 127)
fcr_threshold_green = (30, 100, -64, -8, -32, 32)
fcr_threshold_blue = (45, 65, -20, 30, -60, -20)
fcr_current_threshold = fcr_threshold_green
fcr_max_region_size_detected = 60   # in pixel

while True:
    gc.collect()
    img=sensor.snapshot()

    fcr_blobs = img.find_blobs([fcr_current_threshold], area_threshold=150)
    if fcr_blobs:    
        for b in fcr_blobs:
            if (b[2] > fcr_max_region_size_detected) or ((b[3] > fcr_max_region_size_detected)):
                img.draw_rectangle(b[0:4])
                img.draw_cross(b[5], b[6])
                img.draw_rectangle(b[0], b[1]-20, b[2], 20, color=(255,255,255), fill=True)
                display_cjk_string(img, b[0]+2, b[1]-20+2, "x:"+ str(b[0]) + ", y:"+ str(b[1]), font_size=1, color=(0,0,0))
                # print(b[0:4])
                print(b[0])
                print(b[1])
                print(b[2])
                print(b[3])

    lcd.display(img, oft=(8,8))
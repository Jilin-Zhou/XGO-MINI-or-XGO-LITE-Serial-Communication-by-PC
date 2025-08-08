import sensor, image, time, lcd, gc
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
sensor.set_auto_whitebal(True)
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.run(1)
sensor.skip_frames()

def crd_get_average(histogram):
    sum = 0
    average = 0
    for object in histogram:
       sum = average + object
    average = sum / 8
    return average 

crd_bounding_box_size = (20, 20)
crd_r = [(224//2)-(crd_bounding_box_size[0]//2), (224//2)-(crd_bounding_box_size[1]//2), crd_bounding_box_size[0], crd_bounding_box_size[1]] # 50x50 center of QQVGA.

while True:
    gc.collect()
    img = sensor.snapshot()
    img.draw_rectangle(crd_r)
    hist = img.get_statistics(bins=8,roi=crd_r)
    rgb_value = image.lab_to_rgb((hist.l_mean(),hist.a_mean(),hist.b_mean()))

    # img.draw_string(5, 2, str(rgb_value), color = (rgb_value[0], rgb_value[1], rgb_value[2]), scale = 2, mono_space=False)
    display_cjk_string(img, 5, 2, str(rgb_value), font_size=1, color = (rgb_value[0], rgb_value[1], rgb_value[2]))
    img.draw_rectangle(189, 5, 30, 30, color = (rgb_value[0], rgb_value[1], rgb_value[2]), fill=True)
    img.draw_rectangle((224//2)-(crd_bounding_box_size[0]//2), (224//2)-(crd_bounding_box_size[1]//2), crd_bounding_box_size[0], crd_bounding_box_size[1], color=(150,150,150), fill=False)
    # color = (rgb_value[0], rgb_value[1], rgb_value[2]),
    # print(str('SOF|') + str(rgb_value[0]) + str('|') + str(rgb_value[1]) + str('|') + str(rgb_value[2]) + str('|'))
    # img_len = v.record(img)
    # lcd.direction(lcd.XY_LRDU)
    
    lcd.display(img,oft=(8,8))

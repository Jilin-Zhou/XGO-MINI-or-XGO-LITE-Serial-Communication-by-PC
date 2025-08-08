import sensor, image, time, math, lcd, gc
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
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.run(1)
sensor.skip_frames(30)
sensor.set_auto_whitebal(False)


DETECT_SINGLE_BLACK_LINE = [(0, 40)]
DETECT_SINGLE_WHITE_LINE = [(128, 255)]

DETECT_GRAYSCALE_THRESHOLD = DETECT_SINGLE_BLACK_LINE

DSL_ROIS = [ 
        (0, 162, 224, 20, 0.7),
        (0, 102, 224, 20, 0.3),
        (0, 42, 224, 20, 0.1)
        ]

DSL_weight_sum = 0 
for DSL_r in DSL_ROIS: DSL_weight_sum += DSL_r[4]

while(True):
    gc.collect()
    
    img = sensor.snapshot()

    DSL_centroid_sum = 0
    for DSL_r in DSL_ROIS:
        DSL_blobs = img.find_blobs(DETECT_GRAYSCALE_THRESHOLD, roi=DSL_r[0:4], merge=True)

        if DSL_blobs:
            DSL_most_pixels = 0
            DSL_largest_blob = 0
            for DSL_i in range(len(DSL_blobs)):
                if DSL_blobs[DSL_i].pixels() > DSL_most_pixels:
                    DSL_most_pixels = DSL_blobs[DSL_i].pixels()
                    DSL_largest_blob = DSL_i

            img.draw_cross(DSL_blobs[DSL_largest_blob].cx(), DSL_blobs[DSL_largest_blob].cy())
            display_cjk_string(img, DSL_blobs[DSL_largest_blob].cx()+5, DSL_blobs[DSL_largest_blob].cy()+5, str(DSL_blobs[DSL_largest_blob].cx())+","+str(DSL_blobs[DSL_largest_blob].cy()), font_size=1, color=(255,255,255))

            DSL_centroid_sum += DSL_blobs[DSL_largest_blob].cx() * DSL_r[4]

    DSL_center_pos = (DSL_centroid_sum / DSL_weight_sum)
    DSL_deflection_angle = 0
    DSL_deflection_angle = -math.atan((DSL_center_pos-112)/112)
    DSL_deflection_angle = math.degrees(DSL_deflection_angle)

    if int(DSL_deflection_angle) < 0:
        display_cjk_string(img, 5, 5, "Turn Left", font_size=1, color=(255,255,255))
    elif int(DSL_deflection_angle) > 0:
        # img.draw_string(5, 5, "Turn Right", scale=2, mono_space=False)
        display_cjk_string(img, 5, 5,"Turn Right", font_size=1, color=(255,255,255))
    elif int(DSL_deflection_angle) == 0:
        # img.draw_string(5, 5, "Go Straight", scale=2, mono_space=False)
        display_cjk_string(img, 5, 5, "Go Straight", font_size=1, color=(255,255,255))

    # img.draw_string(5, 5, str(int(DSL_deflection_angle))+" Degree", scale=2, mono_space=False)

    lcd.display(img, oft=(8,8))

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

ROI = (0, 92, 224, 40)

DETECT_SINGLE_BLACK_LINE = [(0, 40)]
DETECT_SINGLE_WHITE_LINE = [(128, 255)]

GRAYSCALE_THRESHOLD = DETECT_SINGLE_BLACK_LINE

def get_blob_value(blob):
    return blob.w()

def compare_blob(blob1, blob2):
    comp_result = get_blob_value(blob1) - get_blob_value(blob2)

    if comp_result > 3:
        return 1
    elif comp_result < -3:
        return -1
    else:
        return 0

def get_direction(left_blob, right_blob):

    MAX_WIDTH = 224
    theta = 0.01
    b = 3

    x1 = left_blob.x() - int(0.5 * left_blob.w())
    x2 = right_blob.x() + int(0.5 * right_blob.w())

    w_left = x1
    w_center = math.fabs(x2 - x1)
    w_right = math.fabs(MAX_WIDTH - x2)

    direct_ratio = (w_left + b + theta * w_center) / (w_left + w_right + 2 * b + 2 * theta * w_center) - 0.5
    return direct_ratio

def get_top2_blobs(blobs):
    for blob in blobs:
        pass
        #print(blob)
        # img.draw_rectangle(blob.rect())

    if len(blobs) < 2:
        return (None, None)

    top_blob1 = blobs[0]
    top_blob2 = blobs[1]

    if compare_blob(top_blob1, top_blob2) == -1:
        top_blob1, top_blob2 = top_blob2, top_blob1


    for i in range(2, len(blobs)):
        if compare_blob(blobs[i], top_blob1) == 1:
            top_blob2 = top_blob1
            top_blob1 = blobs[i]
        elif compare_blob(blobs[i], top_blob2) == 1:
            top_blob2 = blobs[i]

    if top_blob1.cx() > top_blob2.cx():
        return (top_blob2, top_blob1)
    else:
        return (top_blob1, top_blob2)

def draw_direct(img, direct_ratio):
    img.draw_circle(112, 112, 5)
    img.draw_line((112, 112, int(112 + direct_ratio * 20), 112))

while(True):
    gc.collect()
    img = sensor.snapshot() # Take a picture and return the image.

    blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=ROI, merge=True)

    if blobs:
        left_blob, right_blob = get_top2_blobs(blobs)

        if(left_blob == None or right_blob == None):
            print("Out Of Range")
            lcd.display(img, oft=(8,8))
            continue
        else:
            print("left blob")
            print(left_blob)
            print("right blob")
            print(right_blob)

            # img.draw_rectangle(left_blob.rect())
            # img.draw_cross(left_blob.cx(), left_blob.cy())
            img.draw_circle(left_blob.cx(), left_blob.cy(), 3, thickness=2)

            # img.draw_rectangle(right_blob.rect())
            # img.draw_cross(right_blob.cx(), right_blob.cy())
            img.draw_circle(right_blob.cx(), right_blob.cy(), 3, thickness=2)
            img.draw_line(left_blob.cx(), left_blob.cy(), right_blob.cx(), right_blob.cy(), thickness=2)

            direct_ratio = get_direction(left_blob, right_blob)
            display_cjk_string(img, 10, 33, "%.2f"%direct_ratio, font_size=1, color=(255,255,255))

            rect_color = (0,0,255)
            arrow_color = (255,255,255)

            if float(direct_ratio) < -0.1:
                display_cjk_string(img, 10, 10, "Turn Left", font_size=1, color=(255,255,255))
                img.draw_rectangle(174,10,40,40,color=rect_color,fill=True)
                img.draw_arrow(207, 30,180, 30, color=arrow_color, thickness=3)
            elif float(direct_ratio) > 0.1:
                display_cjk_string(img, 10, 10, "Turn Right", font_size=1, color=(255,255,255))
                img.draw_rectangle(174,10,40,40,color=rect_color,fill=True)
                img.draw_arrow(180, 30, 207, 30, color=arrow_color, thickness=3)
            elif int(direct_ratio) == 0:
                display_cjk_string(img, 10, 10, "Go Straight", font_size=1, color=(255,255,255))
                img.draw_rectangle(174,10,40,40,color=rect_color,fill=True)
                img.draw_arrow(194, 40, 194, 20, color=arrow_color, thickness=3)
                

            # draw_direct(img, direct_ratio)

    lcd.display(img, oft=(8,8))

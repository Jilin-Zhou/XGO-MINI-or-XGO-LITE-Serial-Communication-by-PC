from fpioa_manager import *
import os, Maix, lcd, image, sensor, gc, time
from Maix import FPIOA, GPIO
from cocorobo import display_cjk_string

gc.enable()

buttonLeft= 9
buttonRight= 10

fpiol = FPIOA()
fpior = FPIOA()

fpiol.set_function(buttonLeft,FPIOA.GPIO0)
fpior.set_function(buttonRight,FPIOA.GPIO1)

key_gpio_left=GPIO(GPIO.GPIO0,GPIO.IN)
key_gpio_right=GPIO(GPIO.GPIO1,GPIO.IN)

ksl = 0
ksr = 0

total_shot_need_tobe_taken = 200
current_shot_taken = 0

total_classes = 10 # no more than 3
current_class = 1

dataset_folder_name = "dataset"

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(0,0,0)
img = image.Image(size=(240, 240))

display_cjk_string(img, 10, 10, "Image Capture Assistant", font_size=1, color=(0,255,255))
display_cjk_string(img, 10, 35, "For A.I. Training Purpose", font_size=1, color=(0,255,255))
lcd.display(img,oft=(0,0))

time.sleep_ms(1000)
display_cjk_string(img, 10, 190, "Testing Camera...", font_size=1, color=(255,255,255))
lcd.display(img,oft=(0,0))

try: 
    for i in range(1,total_classes+1,1): os.rmdir("/sd/user/"+dataset_folder_name+"/"+str(i))
    os.rmdir("/sd/user/"+dataset_folder_name)
    os.mkdir("/sd/user/"+dataset_folder_name)
except Exception:
    try:
        os.mkdir("/sd/user/"+dataset_folder_name)
    except Exception:
        os.listdir("/sd/user/"+dataset_folder_name)

try:
    for i in range(1,total_classes+1,1): os.mkdir("/sd/user/"+dataset_folder_name+"/"+str(i))
    os.listdir("/sd/user/"+dataset_folder_name)
except Exception:
    print("fail to create directory")

try:
    gc.collect()
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.VGA)
    sensor.set_windowing((448,448))
    sensor.set_vflip(0)
    sensor.set_hmirror(0)
    sensor.set_auto_whitebal(True)
    sensor.set_contrast(0)
    sensor.set_brightness(0)
    sensor.set_saturation(0)
    sensor.run(1)
    gc.collect()

    display_cjk_string(img, 10, 215, "Camera Ready.", font_size=1, color=(0,255,0))
    lcd.display(img,oft=(0,0))
    time.sleep_ms(1000)
    
    img.clear()
    lcd.display(img,oft=(0,0))

except Exception:
    display_cjk_string(img, 10, 215, "Camera initialize failed.", font_size=1, color=(0,255,0))
    lcd.display(img,oft=(0,0))
    img.clear()
    lcd.display(img,oft=(0,0))

def print_current_status():
    print(str(current_class)+"/"+str(total_classes) + ", " +str(current_shot_taken)+"/"+str(total_shot_need_tobe_taken))

while True:
    gc.collect()
    
    img = sensor.snapshot()
    
    img_raw = img.resize(224,224)
    
    a = img_raw.ai_to_pix()

    key_state_left = key_gpio_left.value()
    key_state_right = key_gpio_right.value()

    img_raw.draw_rectangle(0,0,224,24,color=(0,0,0),fill=True)
    img_raw.draw_rectangle(0,200,224,24,color=(0,0,0),fill=True)

    if (key_state_left == 1 and ksl == 0):
        current_class = current_class + 1
        current_shot_taken = 0
        display_cjk_string(img_raw, 0, 0, "Class:"+str(current_class)+"/"+str(total_classes), font_size=1, color=(255,255,255))
        ksl = 1
    elif (key_state_left == 0 and ksl == 1):
        ksl = 0

    if (key_state_right == 1 and ksr == 0):
        print("captured")
        display_cjk_string(img_raw, 0, 0, "Class:"+str(current_class)+"/"+str(total_classes), font_size=1, color=(255,255,255))
        
        image_file_name = str(current_class)+"_"+str(current_shot_taken)+".jpg"
        print(image_file_name)
        gc.collect()
        img = sensor.snapshot()
        img_raw = img.resize(224,224)
        gc.collect()
        a = img_raw.ai_to_pix()
        gc.collect()
        img_raw.save("/sd/user/"+dataset_folder_name+"/"+str(current_class)+"/"+str(image_file_name), quality=90)
        
        img = sensor.snapshot()
        gc.collect()
        img_raw = img.resize(224,224)
        gc.collect()
        a = img_raw.ai_to_pix()
        img_raw.draw_rectangle(0,200,224,24,color=(0,0,0),fill=True)
        display_cjk_string(img_raw, 0, 204, "Saved: "+ str(image_file_name), font_size=1, color=(255,255,0))
        lcd.display(img_raw,oft=(8,8))
        gc.collect()
        time.sleep_ms(500)
        current_shot_taken = current_shot_taken + 1
        ksr = 1
    elif (key_state_right == 0 and ksr == 1):
        ksr = 0

    if current_class > total_classes: current_class = total_classes
    if current_shot_taken > total_shot_need_tobe_taken: current_shot_taken = total_shot_need_tobe_taken

    # print_current_status()
    display_cjk_string(img_raw, 0, 0, "Class:"+str(current_class)+"/"+str(total_classes), font_size=1, color=(255,255,255))
    display_cjk_string(img_raw, 0, 204, "Taking Shot "+ str(current_shot_taken)+" of "+str(total_shot_need_tobe_taken), font_size=1, color=(255,255,255))

    lcd.display(img_raw,oft=(8,8))

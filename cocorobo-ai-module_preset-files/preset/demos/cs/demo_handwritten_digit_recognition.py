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

from fpioa_manager import *
import os, Maix, lcd, image, sensor, gc, time
from Maix import FPIOA, GPIO
from cocorobo import display_cjk_string

gc.enable()
gc.threshold(800000)
gc.collect()

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(0,0,0)


gc.collect()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))    #set to 224x224 input
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.run(1)
sensor.skip_frames(30)

gc.collect()
task_mnist = kpu.load("/sd/preset/models/mnist.kmodel")
gc.collect()
kpu.memtest()

i, j = 0, 0

def debug():
    global i, j
    print(str(i) + ", " + str(j))
    i += 1

while True:
    
    img_mnist = sensor.snapshot()
    debug()
    img_mnist1=img_mnist.to_grayscale(1)        #convert to gray
    debug()
    img_mnist2=img_mnist1.resize(28,28)         #resize to mnist input 28x28
    debug()
    a=img_mnist2.invert()                 #invert picture as mnist need
    debug()
    a=img_mnist2.strech_char(1)           #preprocessing pictures, eliminate dark corner
    debug()
    a=img_mnist2.pix_to_ai()              #generate data for ai
    debug()
    
    fmap_mnist=kpu.forward(task_mnist,img_mnist2)     #run neural network model 
    debug()
    plist_mnist=fmap_mnist[:]                   #get result (10 digit's probability)
    debug()
    pmax_mnist=max(plist_mnist)                 #get max probability
    debug()
    max_index_mnist=plist_mnist.index(pmax_mnist)     #get the digit
    debug()

    # print(str(max_index_mnist)+","+str(int(pmax_mnist*100)))

    img_mnist.draw_rectangle(0,0,45,50,color=(0,0,0),fill=True, thickness=1)
    debug()
    display_cjk_string(img_mnist, 10, 0, str(max_index_mnist), font_size=3, color=(255,255,255))
    debug()
    lcd.display(img_mnist,oft=(8,8))        #display large picture
    debug()
    i = 0
    j += 1

kpu.deinit(task)
import lcd
import image
import sensor
from cocorobo import display_cjk_string


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
qrcode_string = ""

while True:
    camera = sensor.snapshot()
    qrcode_find = camera.find_qrcodes()
    if len(qrcode_find) > 0:
        first_qrcode = qrcode_find[0]
        qrcode_string = first_qrcode.payload()
        camera.draw_rectangle((first_qrcode.x()),(first_qrcode.y()), (first_qrcode.w()), (first_qrcode.h()), color=(255,0,0), thickness=2, fill=False)
        camera.draw_rectangle((first_qrcode.x()),((first_qrcode.y()) - 30), (first_qrcode.w()), 30, color=(255,0,0), thickness=1, fill=True)
        
        display_cjk_string(camera, ((first_qrcode.x()) + 4),((first_qrcode.y()) - 26), (str(qrcode_string)), font_size=1, color=(255,255,255))
    elif len(qrcode_find) <= 0:
        qrcode_string = ""
    print(qrcode_find)
    lcd.display(camera, oft=(8, 8))

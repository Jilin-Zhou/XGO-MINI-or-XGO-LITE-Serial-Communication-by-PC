import lcd
import image
import sensor

import gc

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
sensor.set_auto_whitebal(True)
sensor.set_auto_exposure(True)
sensor.set_windowing((224,224))

gc.collect()

while True:
	gc.collect()
	camera = sensor.snapshot()
	camera.draw_rectangle(40,40, 140, 140, color=(255,255,255), thickness=1, fill=False)
	find_rectangle_result = camera.find_rects(roi=(40, 40,140, 140), threshold = 10000)
	for i in find_rectangle_result:
		camera.draw_rectangle((i.x()),(i.y()), (i.w()), (i.h()), color=(255,0,0), thickness=2, fill=False)
		for k in (i.corners()):
			camera.draw_circle(k[0],k[1], 2, color=(51, 255, 51), thickness=3, fill=False)
	_camera_x, _camera_y = 8, 8
	lcd.display(camera, oft=(_camera_x,_camera_y))

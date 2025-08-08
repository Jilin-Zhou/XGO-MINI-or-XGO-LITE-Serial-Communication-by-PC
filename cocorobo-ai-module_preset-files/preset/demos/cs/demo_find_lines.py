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
	find_line_result = camera.find_lines(roi=(0, 0,224, 224), threshold = 1000, theta_margin = 25, rho_margin = 25)
	for i in find_line_result:
		camera.draw_line((i.x1()),(i.y1()), (i.x2()),(i.y2()), color=(255,0,0), thickness=2)
	_camera_x, _camera_y = 8, 8
	lcd.display(camera, oft=(_camera_x,_camera_y))

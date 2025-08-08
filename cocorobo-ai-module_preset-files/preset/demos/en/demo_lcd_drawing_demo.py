import lcd
import image



lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
canvas = image.Image(size=(240, 240))

while True:
	for i in range(0, 242, 5):
	    canvas.draw_line(0,i, i,240, color=(51,102,255), thickness=1)
	    lcd.display(canvas, oft=(0, 0))
	for i in range(0, 242, 5):
	    canvas.draw_line(i,240, 240,(int((241 - i))), color=(255,0,0), thickness=1)
	    lcd.display(canvas, oft=(0, 0))
	for i in range(0, 242, 5):
	    canvas.draw_line(240,(int((241 - i))), (int((241 - i))),0, color=(102,51,255), thickness=1)
	    lcd.display(canvas, oft=(0, 0))
	for i in range(0, 242, 5):
	    canvas.draw_line((int((241 - i))),0, 0,i, color=(255,0,0), thickness=1)
	    lcd.display(canvas, oft=(0, 0))

	canvas.clear()

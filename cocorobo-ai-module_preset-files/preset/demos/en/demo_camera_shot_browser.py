from fpioa_manager import *
import os, Maix, lcd, image, sensor, gc, time
from Maix import FPIOA, GPIO
from cocorobo import display_cjk_string

gc.enable()

buttonLeft, buttonRight = 9, 10

fpiol = FPIOA()
fpior = FPIOA()

fpiol.set_function(buttonLeft,FPIOA.GPIO0)
fpior.set_function(buttonRight,FPIOA.GPIO1)

key_gpio_left=GPIO(GPIO.GPIO0,GPIO.IN)
key_gpio_right=GPIO(GPIO.GPIO1,GPIO.IN)

ksl,ksr = 0, 0

button_count = 0
lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(0,0,0)

current_showing = 1
shot_count = 1

def showing_photo(count):
	global showing_resized
	showing_photo = image.Image("/sd/user/camera/cocoshot"+ str(count) +".jpg")
	showing_resized = showing_photo.resize(224,224)
	showing_resized.draw_rectangle(0,0,224,20,fill=True,color=(0,0,0))
	display_cjk_string(showing_resized, 0, 0, "Displaying "+str(current_showing) + " of " + str(shot_count), font_size=1, color=(255,255,255))
	lcd.display(showing_resized, oft=(8,8))


shot_count_ls = os.listdir("/sd/user/camera")
print(shot_count_ls)

for i in shot_count_ls:
	if "cocoshot" not in i or "._" in i:
		print(str(i))
		os.remove("/sd/user/camera/"+str(i))

shot_count_ls = os.listdir("/sd/user/camera")
print(shot_count_ls)

shot_count = len(os.listdir("/sd/user/camera"))
print(shot_count)

showing_photo(current_showing)

while True:
	gc.collect()
	# print(str(gc.mem_free()/1000)+"kb")
	# os.listdir("/sd/user/camera")
	
	# print(shot_count)
	# lcd.draw_string(8,5, "Displaying "+str(current_showing) + " of " + str(shot_count-1), lcd.WHITE, lcd.BLACK)

	key_state_left = key_gpio_left.value()
	key_state_right = key_gpio_right.value()

	if (key_state_left == 1 and ksl == 0):
		current_showing = current_showing - 1
		if current_showing <= 0: current_showing = 1
		print("left pressed, current: " + str(current_showing))
		showing_photo(current_showing)

		ksl = 1
	elif (key_state_left == 0 and ksl == 1): ksl = 0

	if (key_state_right == 1 and ksr == 0):
		current_showing = current_showing + 1
		if current_showing > shot_count: current_showing = shot_count
		print("right pressed " + str(current_showing))
		showing_photo(current_showing)

		ksr = 1
	elif (key_state_right == 0 and ksr == 1): ksr = 0 





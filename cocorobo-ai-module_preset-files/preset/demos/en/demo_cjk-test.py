import lcd, image, time
from cocorobo import display_cjk_string

img = image.Image(size=(240, 240))

lcd.init(type=2,freq=19000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)

y = 10
col = 10
is_bottom = False

while True:

	img.clear()

	display_cjk_string(img, col, y, "細草微風岸，危檣獨夜舟。", font_size=1, color=(255,255,255))
	display_cjk_string(img, col, y+25, "星垂平野闊，月涌大江流。", font_size=1, color=(255,255,255))
	display_cjk_string(img, col, y+50, "— 杜甫《旅夜書懷》", font_size=1, color=(150,150,150))

	display_cjk_string(img, col, y+90, "一个人的行走范围，", font_size=1, color=(255,255,255))
	display_cjk_string(img, col, y+115, "就是他的世界。", font_size=1, color=(255,255,255))
	display_cjk_string(img, col, y+140, "— 北島", font_size=1, color=(150,150,150))

	display_cjk_string(img, col, y+180, "今夜は月が綺麗ですね。", font_size=1, color=(255,255,255))
	display_cjk_string(img, col, y+205, "— 夏目漱石", font_size=1, color=(150,150,150))

	display_cjk_string(img, col, y+245, "사람이 온다는 건은", font_size=1, color=(255,255,255))
	display_cjk_string(img, col, y+270, "실은 어마어마한 일이다.", font_size=1, color=(255,255,255))
	display_cjk_string(img, col, y+295, "— 정현종/郑玄宗《방문객》", font_size=1, color=(150,150,150))

	time.sleep_ms(10)

	if y <= -90:
		y = 10
		lcd.display(img)
		time.sleep(2)
	elif y > -90 and y < 10:
		y -= 2
		lcd.display(img)
	elif y == 10:
		lcd.display(img)
		time.sleep(2)
		y -= 2



'''
cocorobo_draw_text_new(0, 0, img, roman_text[0][0:8], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 35, img, roman_text[0][8:16], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 70, img, roman_text[0][16:len(roman_text[0])], size=2, color=(255,255,255))

cocorobo_draw_text_new(0, 105, img, roman_text[1][0:10], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 140, img, roman_text[1][10:18], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 175, img, roman_text[1][18:len(roman_text[1])], size=2, color=(255,255,255))

lcd.display(img)
img.clear()
time.sleep(1)

cocorobo_draw_text_new(0, 0, img, roman_text[2], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 35, img, roman_text[3][0:9], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 70, img, roman_text[3][9:20], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 105, img, roman_text[3][20:len(roman_text[3])], size=2, color=(255,255,255))
cocorobo_draw_text_new(0, 140, img, mixed_text, size=2, color=(255,255,255))

lcd.display(img)
time.sleep(1)
'''

'''

count = 0

while True:
	count += 1
	print(count)
	for i in range(0,12,1):
		display_cjk_string(img, 0, i*20, alphabet_lower, font_size=1, color=(255,255,255))
		lcd.display(img)
	for i in range(0,12,1):
		display_cjk_string(img, 0, i*20, alphabet_lower, font_size=1, color=(0,0,0))
		lcd.display(img)
'''
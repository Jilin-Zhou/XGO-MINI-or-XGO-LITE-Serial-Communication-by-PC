import video, lcd, image
try:from cocorobo import display_cjk_string
except:pass
from Maix import GPIO
import os, time

lcd.init(type=2)
lcd.rotation(1)
lcd.clear(lcd.BLACK)
canvas = image.Image(size=(240, 240))

def lcd_draw_string(canvas, x, y, text, color=(255,255,255), font_size=1, scale=1, mono_space=False, auto_wrap=True):
    try:
        if font_size == 1 and scale != 1: font_size = scale
        else: font_size = font_size
        display_cjk_string(canvas, x, y, text, font_size=font_size, color=color)
        return canvas
    except: return canvas.draw_string(x, y, text, color=color, scale=scale, mono_space=mono_space)

_video_play = video.open("/sd/user/record.avi")
while True:
    if (_video_play.play()) == False:
        break
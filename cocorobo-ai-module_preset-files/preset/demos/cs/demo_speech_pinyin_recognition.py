from cocorobo import mandarin_asr
import lcd
import image

try:from cocorobo import display_cjk_string
except:pass

def lcd_draw_string(canvas, x, y, text, color=(255,255,255), font_size=1, scale=1, mono_space=False, auto_wrap=True):
    try:
        if font_size == 1 and scale != 1: font_size = scale
        else: font_size = font_size
        display_cjk_string(canvas, x, y, text, font_size=font_size, color=color)
        return canvas
    except: return canvas.draw_string(x, y, text, color=color, scale=scale, mono_space=mono_space)

lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)

canvas = image.Image(size=(240, 240))
_canvas_x, _canvas_y = 0, 0

asr = mandarin_asr(
    config = {
        "ni-hao": 0.1,
        "zai-jian": 0.1,
        "bai-bai": 0.1,
        "lao-shi-hao": 0.1,
        "zao-an": 0.1,
        "wan-an": 0.1,
        "xie-xie": 0.1,
        "wan-shi-ru-yi": 0.1,
        "ke-ke-le-bo": 0.1,
        "shen-zhen": 0.1,
        "xiang-gang": 0.1,
        "chong-qi": 0.1
    },
    timer = (2,0)
)

vocabulary_list = {
    "ni-hao": "你好",
    "zai-jian": "再见",
    "bai-bai": "拜拜",
    "lao-shi-hao": "老师好",
    "zao-an": "早安",
    "wan-an": "晚安",
    "xie-xie": "谢谢",
    "wan-shi-ru-yi": "万事如意",
    "ke-ke-le-bo": "可可乐博",
    "shen-zhen": "深圳",
    "xiang-gang": "香港",
    "chong-qi": "重启"
}

while True:
    lcd_draw_string(canvas,55, 5, "普通话识别演示", color=(255,255,255), scale=1, mono_space=False)

    lcd_draw_string(canvas, 48, 120-10, "结果将在上框出现", color=(100,100,100), scale=1, mono_space=False)
    canvas.draw_rectangle(40, 50-10, 160, 60, color=(100,100,100), thickness=1, fill=False)

    canvas.draw_line(5,142, 235,142, color=(100,100,100), thickness=1)
    lcd_draw_string(canvas,5, 152, "请使用普通话说出以下单词:", color=(255,255,255), scale=1, mono_space=False)
    lcd_draw_string(canvas,5, 152+22*1, "你好、再见、拜拜、老师好", color=(0,255,255), scale=1, mono_space=False)
    lcd_draw_string(canvas,5, 152+22*2, "早安、晚安、谢谢、万事如意", color=(0,255,255), scale=1, mono_space=False)
    lcd_draw_string(canvas,5, 152+22*3, "可可乐博、深圳、香港、重启", color=(0,255,255), scale=1, mono_space=False)

    lcd.display(canvas, oft=(_canvas_x,_canvas_y))

    recognition_text = asr.getRecognizeResult()
    print(recognition_text)
    type(recognition_text)

    canvas.draw_rectangle(40, 50-10, 160, 60, color=(0,0,0), thickness=1, fill=True)
    canvas.draw_rectangle(40, 50-10, 160, 60, color=(100,100,100), thickness=1, fill=False)
    lcd_draw_string(canvas, 50, 60-10, vocabulary_list[recognition_text], color=(0,255,255), scale=2, mono_space=False)
    lcd.display(canvas, oft=(_canvas_x,_canvas_y))

    if recognition_text == "chong-qi":
        lcd_draw_string(canvas, 50, 60-10, vocabulary_list[recognition_text], color=(255,0,0), scale=2, mono_space=False)
        lcd.display(canvas, oft=(_canvas_x,_canvas_y))
        time.sleep(0.5)
        import machine
        machine.reset()


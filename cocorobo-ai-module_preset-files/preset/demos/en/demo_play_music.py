from Maix import I2S, GPIO
from fpioa_manager import *
import audio

import lcd, image, time
from cocorobo import display_cjk_string

img = image.Image(size=(240, 240))

lcd.init(type=2,freq=19000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)

_audio_rx = I2S(I2S.DEVICE_0)
_player = audio.Audio(path = "/sd/preset/songs/doraemon.wav")
_player.volume(90)
_wav_info = _player.play_process(_audio_rx)
_audio_rx.channel_config(_audio_rx.CHANNEL_1, I2S.TRANSMITTER, resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
_audio_rx.set_sample_rate(_wav_info[1])
_audio_play_state = 0

fm.register(34,fm.fpioa.I2S0_OUT_D1)
fm.register(35,fm.fpioa.I2S0_SCLK)
fm.register(33,fm.fpioa.I2S0_WS)

while True:
    _audio_play_state = _player.play()

    display_cjk_string(img, 10, 10, "Playing: doraemon.wav", font_size=1, color=(255,255,255))
    lcd.display(img)

    if (_audio_play_state) == True:
        print("Playing.")
    elif (_audio_play_state) == False:
        print("Done.")
        display_cjk_string(img, 10, 10, "Playing: doraemon.wav", font_size=1, color=(100,100,100))
        display_cjk_string(img, 10, 35, "Stopped.", font_size=1, color=(255,0,0))
        lcd.display(img)
        break

import machine
machine.reset()

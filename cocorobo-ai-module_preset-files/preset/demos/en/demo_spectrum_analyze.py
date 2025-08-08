import lcd
import image
from Maix import GPIO, I2S, FFT
from board import board_info
from fpioa_manager import fm

sample_rate = 38640
sample_points = 1024
fft_points = 512
hist_x_num = 50

fm.register(20,fm.fpioa.I2S0_IN_D0, force=True)
fm.register(19,fm.fpioa.I2S0_WS, force=True)
fm.register(18,fm.fpioa.I2S0_SCLK, force=True)

_recorder_rx = I2S(I2S.DEVICE_0)
_recorder_rx.channel_config(_recorder_rx.CHANNEL_0, _recorder_rx.RECEIVER, align_mode = I2S.STANDARD_MODE)
_recorder_rx.set_sample_rate(sample_rate)
def _microphone_read_average(lst):
    return int((sum(lst)/len(lst))*100)

sample_rate = 38640
sample_points = 1024
fft_points = 512
hist_x_num = 50

read_all_channel = [0, 0, 0, 0, 0, 0, 0, 0]



lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
lcd.clear(lcd.BLACK)
canvas = image.Image("/sd/preset/images/splash_bg.jpg")
while True:
    _audio = _recorder_rx.record(sample_points)
    fft_res = FFT.run(_audio.to_bytes(),fft_points)
    fft_amp = FFT.amplitude(fft_res)

    read_all_channel[0] = int(_microphone_read_average(fft_amp[0:63]))
    read_all_channel[1] = int(_microphone_read_average(fft_amp[64:127]))
    read_all_channel[2] = int(_microphone_read_average(fft_amp[127:191]))
    read_all_channel[3] = int(_microphone_read_average(fft_amp[192:255]))
    read_all_channel[4] = int(_microphone_read_average(fft_amp[256:319]))
    read_all_channel[5] = int(_microphone_read_average(fft_amp[320:383]))
    read_all_channel[6] = int(_microphone_read_average(fft_amp[384:447]))
    read_all_channel[7] = int(_microphone_read_average(fft_amp[448:514]))
    radius1 = int(((read_all_channel[0]) / 10))
    radius2 = int(((read_all_channel[1]) / 10))
    radius3 = int(((read_all_channel[2]) / 10))
    radius4 = int(((read_all_channel[3]) / 20))
    radius5 = int(((read_all_channel[4]) / 20))
    radius6 = int(((read_all_channel[5]) / 20))
    print((str(radius1)))
    canvas.clear()
    canvas.draw_circle(120,120, radius1, color=(255, 0, 0), thickness=2, fill=True)
    canvas.draw_circle(120,120, radius2, color=(51, 102, 255), thickness=5, fill=False)
    canvas.draw_circle(120,120, radius2, color=(0, 0, 153), thickness=5, fill=False)
    lcd.display(canvas, oft=(0, 0))

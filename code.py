# code.py - 本地想要上传的代码脚本
# Code scripts that you want to upload locally
# author: Jilin Zhou
# 2025.08.06

# 注意：请务必核对机器狗的内置库为luwudynamic的xgolib系列还是cocorobo的ai开发板系列，二者的代码有所区别
# Note: Please be sure to check whether the built-in library of the robot dog is Luwudynamic's XGOLIB series or Cocorobo's AI development board series, the code of the two is different

import machine, time
from fpioa_manager import fm
try:
	from xgo import XGO
except BaseException as e:
	print(str(e))
	pass

fm.register(13,fm.fpioa.UART2_TX)
fm.register(14,fm.fpioa.UART2_RX)
dog = XGO(machine.UART.UART2, 115200, "xgolite")


# 原地踏步5s
# Stand in place for 5s
dog.mark_time(22)
time.sleep(5)
dog.mark_time(0)
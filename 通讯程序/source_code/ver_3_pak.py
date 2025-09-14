import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import serial.tools.list_ports
import os
import threading
import time
import base64
from google import genai


DOG_PORT = 'COM7' # 默认值
LOCAL_TEMP_FILE = 'user_input_code.py' # 用于暂存用户输入的代码
REMOTE_FILE_PATH = 'user_latest_code.py' # 上传到机器狗上的文件名

SYSTEM_PROMPT = """
You are a code generation engine for the XGO-Lite robot on the MaixPy platform. You are an expert in both robot motion control and computer vision.
Your response MUST be ONLY the raw, complete, and runnable Python code.
DO NOT include explanatory text or comments unless they are part of a provided template.
DO NOT use Markdown formatting like ```python.
Your response must begin with import machine, time.
Always start with the full, relevant initialization templates.

Knowledge Base
1. Mandatory Initialization Templates
1.1 Robot Initialization
When robot movement is needed, start with this template.

# Import necessary libraries
import machine
import time
from fpioa_manager import fm
from xgo import XGO

# Configure Robot UART
fm.register(13, fm.fpioa.UART2_TX)
fm.register(14, fm.fpioa.UART2_RX)
dog = XGO(machine.UART.UART2, 115200, "xgolite")
dog.reset()
time.sleep(2)
1.2 Screen Display Initialization
When screen display is needed, add this template.

# Import Vision Libraries
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


# Configure LCD
lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
canvas = image.Image(size=(240, 240))
_canvas_x, _canvas_y = 0, 0

1.3 Camera Initialization
Only when camera is needed, add this template.
# Import Vision Libraries
import lcd
import image
import sensor

# Configure LCD and Camera 
lcd.init(type=2,freq=15000000,width=240,height=240,color=(0,0,0))
lcd.rotation(1)
lcd.clear(lcd.BLACK)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA) # 320x240
sensor.set_windowing((224, 224)) # Center crop to 224x224
sensor.skip_frames(30)
sensor.run(1)

2. API Reference
2.1 Robot Control API
Forward/Backward: dog.move('x', speed) (speed>0: Fwd, speed<0: Bwd)

Strafe Left/Right: dog.move('y', speed) (speed>0: Left, speed<0: Right)

Turn Left/Right: dog.turn(speed) (speed>0: Left, speed<0: Right)

Stop: dog.stop()

Pitch (Nod): dog.attitude('p', angle) (angle<0: Down, angle>0: Up)

Height: dog.translation('z', distance) (distance>0: Lowers, distance<0: Raises)

Pre-set Actions: dog.action(id) (e.g., 1: Lie down, 12: Sit, 13: Wave hand, 255: Reset)

Reset Pose: dog.reset()

2.2 Vision & Display API
Capture Image: img = sensor.snapshot() (Captures an image object for processing)

Display Image: lcd.display(img) (Displays the image object on the screen)

Find Circles: circles = img.find_circles(roi, threshold=2500, r_min=10, r_max=100)

Returns a list of circle objects. Access with for c in circles:.

Circle properties: c.x() (center x), c.y() (center y), c.r() (radius).

Find Rectangles: rects = img.find_rects(roi, threshold=10000)

Returns a list of rectangle objects. Access with for r in rects:.

Rectangle properties: r.rect() (returns tuple (x, y, w, h)).

Draw Circle on Image: img.draw_circle(x, y, radius, color=(255,0,0), thickness=2)

Draw Rectangle on Image: img.draw_rectangle(x, y, w, h, color=(255,0,0), thickness=2) or img.draw_rectangle(r.rect(), ...)

Draw Text on Image: img.draw_string(x, y, "Text", color=(255,255,255), scale=2)

3. Critical Rules
Invalid Functions: Do not use dog.stand() or dog.sit(). Use dog.reset() or dog.action(id).

Delays: Always use time.sleep(seconds) after a robot action to allow it to complete.

Main Loop: Vision tasks must be performed inside a while True: loop. Always capture a fresh image with sensor.snapshot() at the start of each loop iteration.

Sign Conventions: Adhere to the sign conventions for direction and speed in the Robot Control API.

Based on all the provided knowledge, process the user's final request.
"""


def generate_xgo_code_gemini(user_command, api_key, model_name="gemini-2.5-flash"):
    client = genai.Client(api_key=api_key)
    full_prompt = SYSTEM_PROMPT + "\n\nUser Request: " + user_command
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"API 调用失败: {e}"

def flatten_code(code_str: str) -> str:
    lines = []
    for line in code_str.strip().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return ";".join(lines)

def execute_remote_command(ser, command_bytes, timeout=10):
    ser.write(command_bytes)
    ser.write(b'\x04')

    response = b''
    start_time = time.time()
    while not response.endswith(b'\x04>'):
        if time.time() - start_time > timeout:
            return False, b"Timeout"
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.01)

    if b'Traceback' in response or b'Error' in response:
        return False, response

    return True, response

class XGOGUIApp:
    def __init__(self, master):
        self.master = master
        master.title("XGO-MINI 智能控制台(made by BUPT Jilin_ZHOU)")
        master.geometry("800x700")

        self.api_key = tk.StringVar()
        self.selected_port = tk.StringVar()
        self.selected_file_path = tk.StringVar()
        self.return_to_main = tk.BooleanVar(value=True) # 默认返回 main.py

        self._create_widgets()
        self._load_config() # 尝试加载保存的配置
        self._update_port_list() # 初始化时更新端口列表

    def _create_widgets(self):
        # API Key 设置
        api_frame = tk.LabelFrame(self.master, text="Gemini API Key 设置(需要全局代理才能使用ai功能)", padx=10, pady=10)
        api_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(api_frame, text="API Key:").pack(side="left")
        self.api_key_entry = tk.Entry(api_frame, textvariable=self.api_key, width=50, show="*")
        self.api_key_entry.pack(side="left", padx=5)
        tk.Button(api_frame, text="保存 Key", command=self._save_api_key).pack(side="left")

        # 串口设置
        port_frame = tk.LabelFrame(self.master, text="机器狗串口设置", padx=10, pady=10)
        port_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(port_frame, text="选择串口:").pack(side="left")
        self.port_menu = tk.OptionMenu(port_frame, self.selected_port, "")
        self.port_menu.pack(side="left", padx=5)
        tk.Button(port_frame, text="刷新串口", command=self._update_port_list).pack(side="left")
        tk.Button(port_frame, text="检测连接", command=self._check_port_connection).pack(side="left", padx=5)

        # 代码上传与执行
        upload_frame = tk.LabelFrame(self.master, text="上传本地代码到机器狗", padx=10, pady=5)
        upload_frame.pack(fill="x", padx=10, pady=5)

        tk.Entry(upload_frame, textvariable=self.selected_file_path, width=60, state="readonly").pack(side="left", padx=5)
        tk.Button(upload_frame, text="选择文件", command=self._select_file).pack(side="left")
        tk.Button(upload_frame, text="上传并运行", command=self._run_uploaded_file_threaded).pack(side="left", padx=5)

        # 大模型对话与代码执行
        ai_frame = tk.LabelFrame(self.master, text="AI 代码生成与执行", padx=10, pady=5)
        ai_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(ai_frame, text="输入指令:").pack(side="left")
        self.ai_command_entry = tk.Entry(ai_frame, width=60)
        self.ai_command_entry.pack(side="left", padx=5)
        tk.Button(ai_frame, text="生成代码并运行", command=self._generate_and_run_code_threaded).pack(side="left", padx=5)

        # 选项：是否返回 main.py
        option_frame = tk.Frame(self.master, padx=10, pady=5)
        option_frame.pack(fill="x", padx=10, pady=5)
        tk.Checkbutton(option_frame, text="代码执行完毕后返回 main.py", variable=self.return_to_main).pack(side="left")

        # 输出日志区域
        log_frame = tk.LabelFrame(self.master, text="日志输出", padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=90, height=20)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled") # 默认不可编辑

    def _log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # 自动滚动到最新消息
        self.log_text.config(state="disabled")

    def _save_api_key(self):
        # 这里为了方便，直接保存在一个配置文件中，肯定还是需要加密最安全
        try:
            with open("config.ini", "w") as f:
                f.write(f"api_key={self.api_key.get()}\n")
                f.write(f"port={self.selected_port.get()}\n") # 保存当前选中的端口
            messagebox.showinfo("保存成功", "API Key 和端口设置已保存！")
            self._log("API Key 和端口设置已保存。")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存配置失败: {e}")
            self._log(f"保存配置失败: {e}")

    def _load_config(self):
        try:
            if os.path.exists("config.ini"):
                with open("config.ini", "r") as f:
                    for line in f:
                        if line.startswith("api_key="):
                            self.api_key.set(line.split("=", 1)[1].strip())
                        elif line.startswith("port="):
                            self.selected_port.set(line.split("=", 1)[1].strip())
                self._log("已加载保存的 API Key 和端口设置。")
        except Exception as e:
            self._log(f"加载配置失败: {e}")

    def _update_port_list(self):
        ports = serial.tools.list_ports.comports()
        port_names = [port.device for port in ports]
        self.port_menu['menu'].delete(0, 'end') # 清空现有菜单

        if not port_names:
            self.selected_port.set("无可用串口")
            self._log("未检测到可用串口。")
        else:
            if self.selected_port.get() not in port_names:
                self.selected_port.set(port_names[0]) # 默认选择第一个
            for port in port_names:
                self.port_menu['menu'].add_command(label=port, command=tk._setit(self.selected_port, port))
            self._log(f"已刷新串口列表，检测到 {len(port_names)} 个串口。")

    def _check_port_connection(self):
        port = self.selected_port.get()
        if not port or port == "无可用串口":
            messagebox.showwarning("端口错误", "请选择一个有效的串口！")
            self._log("未选择有效串口，无法检测连接。")
            return

        self._log(f"正在检测端口 {port} 连接...")
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            ser.close()
            messagebox.showinfo("连接成功", f"端口 {port} 连接正常！")
            self._log(f"端口 {port} 连接正常。")
        except serial.SerialException as e:
            messagebox.showerror("连接失败", f"无法连接到端口 {port}: {e}")
            self._log(f"无法连接到端口 {port}: {e}")

    def _select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择要上传的 Python 文件",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_file_path.set(file_path)
            self._log(f"已选择文件: {file_path}")

    def _run_uploaded_file_threaded(self):
        # 使用线程避免 GUI 卡死
        threading.Thread(target=self._run_uploaded_file).start()

    def _run_uploaded_file(self):
        port = self.selected_port.get()
        local_path = self.selected_file_path.get()
        api_key_val = self.api_key.get()

        if not port or port == "无可用串口":
            messagebox.showwarning("端口错误", "请选择一个有效的串口！")
            self._log("未选择有效串口，无法上传运行。")
            return
        if not local_path:
            messagebox.showwarning("文件错误", "请选择一个本地 Python 文件！")
            self._log("未选择本地文件，无法上传运行。")
            return
        # if not api_key_val:
        #     messagebox.showwarning("API Key 错误", "请设置 Gemini API Key！")
        #     self._log("未设置 API Key。")
            # 即使没有API Key，也可以上传本地文件，这里可以根据需求调整是否强制要求API Key
            # 如果只是运行本地文件，API Key不是必须的。

        self._log(f"\n--- 开始上传并运行本地文件: {local_path} ---")

        # 1. 上传文件
        upload_success = self._upload_code_to_dog(port, local_path, REMOTE_FILE_PATH)
        if not upload_success:
            self._log("文件上传失败，已取消远程执行。")
            return

        # 2. 执行远程文件
        self._execute_remote_file(port, REMOTE_FILE_PATH, self.return_to_main.get())
        self._log("--- 本地文件上传并运行流程结束 ---")

    def _generate_and_run_code_threaded(self):
        # 使用线程避免 GUI 卡死
        threading.Thread(target=self._generate_and_run_code).start()

    def _generate_and_run_code(self):
        command = self.ai_command_entry.get()
        api_key_val = self.api_key.get()
        port = self.selected_port.get()

        if not command:
            messagebox.showwarning("指令错误", "请输入要给机器狗的指令！")
            self._log("未输入指令，无法生成代码。")
            return
        if not api_key_val:
            messagebox.showwarning("API Key 错误", "请设置 Gemini API Key！")
            self._log("未设置 API Key，无法调用大模型。")
            return
        if not port or port == "无可用串口":
            messagebox.showwarning("端口错误", "请选择一个有效的串口！")
            self._log("未选择有效串口，无法运行代码。")
            return

        self._log(f"\n--- 正在为指令生成代码: '{command}' ---")
        generated_code = generate_xgo_code_gemini(command, api_key_val)

        if "API 调用失败" in generated_code:
            self._log(f"代码生成失败: {generated_code}")
            messagebox.showerror("代码生成失败", generated_code)
            return

        self._log("\n--- 生成的代码 ---")
        self._log(generated_code)
        self._log("------------------")

        # 1. 将生成的代码写入本地临时文件
        try:
            with open(LOCAL_TEMP_FILE, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            self._log(f"代码已成功写入本地文件 '{LOCAL_TEMP_FILE}'。")
        except Exception as e:
            self._log(f"  [失败] 写入本地文件失败: {e}")
            messagebox.showerror("写入文件失败", f"写入本地文件失败: {e}")
            return

        # 2. 上传文件到机器狗
        upload_success = self._upload_code_to_dog(port, LOCAL_TEMP_FILE, REMOTE_FILE_PATH)
        if not upload_success:
            self._log("文件上传失败，已取消远程执行。")
            return

        # 3. 执行远程文件
        self._execute_remote_file(port, REMOTE_FILE_PATH, self.return_to_main.get())
        self._log("--- AI 代码生成与运行流程结束 ---")

    # 稍作修改以适应GUI的日志输出
    def _upload_code_to_dog(self, port, local_path, remote_path):
        self._log(f"\n--- 开始上传文件: {local_path} -> {remote_path} ---")
        if not os.path.exists(local_path):
            self._log(f"错误: 本地文件 '{local_path}' 不存在！")
            return False

        try:
            with open(local_path, 'rb') as f:
                file_data = f.read()
            encoded_data_str = base64.b64encode(file_data).decode('ascii')
        except Exception as e:
            self._log(f"读取或编码本地文件失败: {e}")
            return False

        ser = None
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            self._log("1. 串口已连接。")

            # 进入 Raw REPL
            self._log("2. 进入 Raw REPL...")
            ser.write(b'\x03'); time.sleep(0.1); ser.read_all()  # 中断
            ser.write(b'\x01'); time.sleep(0.1); ser.read_all()  # Raw REPL

            # 准备写入
            self._log(f"3. 准备写入远程文件 '{remote_path}'...")
            cmd = f"import ubinascii; f = open('{remote_path}', 'wb')"
            success, resp = execute_remote_command(ser, cmd.encode('utf-8'))
            if not success:
                self._log(f"  [失败] 打开远程文件失败: {resp.decode(errors='ignore')}")
                return False

            # 分块传输
            chunk_size = 64
            chunks = [encoded_data_str[i:i + chunk_size] for i in range(0, len(encoded_data_str), chunk_size)]
            for i, chunk in enumerate(chunks):
                self._log(f"   传输块 {i + 1}/{len(chunks)}...")
                cmd = f"f.write(ubinascii.a2b_base64(b'{chunk}'))"
                success, resp = execute_remote_command(ser, cmd.encode('utf-8'))
                if not success:
                    self._log(f"  [失败] 写入块失败: {resp.decode(errors='ignore')}")
                    execute_remote_command(ser, b'f.close()') # 尝试关闭文件
                    return False
                time.sleep(0.05)

            # 关闭文件
            execute_remote_command(ser, b'f.close()')
            self._log("4. 文件传输完成。")

            # 验证文件大小
            cmd = f"import os; print(os.stat('{remote_path}')[6])"
            success, resp = execute_remote_command(ser, cmd.encode('utf-8'))
            if success:
                try:
                    remote_size_str = resp.split(b'OK')[1].split(b'\r\n')[0].strip()
                    if int(remote_size_str) == len(file_data):
                        self._log(f"5. 文件验证成功 (大小: {len(file_data)} 字节)。")
                        ser.write(b'\x02')  # 退出 Raw REPL
                        time.sleep(0.1)
                        return True
                    else:
                        self._log(f"  [失败] 文件大小不匹配！远程: {remote_size_str}，本地: {len(file_data)}")
                        return False
                except Exception as e:
                    self._log(f"  [失败] 解析远程文件大小失败: {e}, 原始响应: {resp}")
                    return False
            else:
                self._log(f"  [失败] 验证文件失败: {resp.decode(errors='ignore')}")
                return False

        except serial.SerialException as e:
            self._log(f"错误: 串口操作失败: {e}")
            return False
        finally:
            if ser and ser.is_open:
                ser.close()
                self._log("--- 文件上传流程结束，串口已关闭 ---")


    def _execute_remote_file(self, port, remote_path, return_to_main_flag):
        self._log(f"\n--- 开始远程执行文件: {remote_path} ---")
        ser = None
        try:
            ser = serial.Serial(port, 115200, timeout=2)
            self._log("1. 串口已连接。")
            # 中断可能正在运行的程序 (如 main.py)
            ser.write(b'\x03')
            time.sleep(0.2)
            ser.read_all()
            self._log("2. 已发送中断信号。")

            # 构建并发送执行命令
            exec_command = f"exec(open('{remote_path}').read())\r\n"
            ser.write(exec_command.encode('utf-8'))
            self._log(f"3. 执行指令已发送。机器狗正在执行 '{remote_path}'...")

            # 等待一段时间让脚本执行，并读取输出
            # 这里的sleep时间可能需要用户根据自己的代码调整，或者加入更智能的结束判断
            start_time = time.time()
            output_buffer = b""
            while time.time() - start_time < 15: # 延长等待时间，以便获取更多输出
                if ser.in_waiting > 0:
                    output_buffer += ser.read(ser.in_waiting)
                    # 尝试解码并更新日志，避免阻塞
                    try:
                        decoded_output = output_buffer.decode(errors='ignore')
                        if decoded_output:
                            self._log("设备输出: " + decoded_output.strip())
                        output_buffer = b"" # 清空已处理的 buffer
                    except UnicodeDecodeError:
                        pass # 等待更多字节再尝试解码
                time.sleep(0.1)

            final_output = output_buffer.decode(errors='ignore')
            if final_output:
                self._log("剩余设备输出: " + final_output.strip())

            if return_to_main_flag:
                # 返回主菜单
                self._log("4. 执行完毕，正在尝试返回主菜单...")
                ser.write(b'\x03') # 发送中断
                time.sleep(0.2)
                ser.read_all() # 清空buffer
                ser.write("exec(open('main.py').read())\r\n".encode('utf-8'))
                self._log("已发送返回 main.py 命令。")
            else:
                self._log("4. 执行完毕，未返回 main.py (用户选择)。")
                ser.write(b'\x03') # 至少发个中断，让狗停止当前脚本

        except serial.SerialException as e:
            self._log(f"错误: 远程执行失败: {e}")
            messagebox.showerror("执行失败", f"远程执行失败: {e}")
        except Exception as e:
            self._log(f"发生未知错误: {e}")
            messagebox.showerror("未知错误", f"发生未知错误: {e}")
        finally:
            if ser and ser.is_open:
                ser.close()
                self._log("--- 远程执行流程结束，串口已关闭 ---")


if __name__ == "__main__":
    root = tk.Tk()
    app = XGOGUIApp(root)
    root.mainloop()
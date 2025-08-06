# uploader.py - 使用Base64编码和二进制写入的高可靠性上传脚本
# Upload scripts with high reliability using Base64 encoding and binary writes
# author: Jilin Zhou
# 2025.08.06

import serial
import time
import os
import base64

PORT = 'COM7'  # 端口
LOCAL_FILE_PATH = 'code.py'  # 本地文件名
REMOTE_FILE_PATH = 'user_latest_code.py'

CTRL_A = b'\x01'  # 进入 Raw REPL
CTRL_B = b'\x02'  # 退出 Raw REPL
CTRL_C = b'\x03'  # 中断
CTRL_D = b'\x04'  # 执行


def execute_remote_command(ser, command_bytes, timeout=10):
    """发送命令并严格检查响应"""
    ser.write(command_bytes)
    ser.write(CTRL_D)

    response = b''
    start_time = time.time()
    while not response.endswith(b'\x04>'):
        if time.time() - start_time > timeout:
            return False, b"Timeout"
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.01)

    if b'Traceback' in response or b'Error' in response:
        return False, response  # 如果有错误，返回失败

    return True, response


def main():
    print("--- 上传脚本测试(Base64模式) ---")

    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"错误: 本地文件 '{LOCAL_FILE_PATH}' 不存在！")
        return

    # 读取本地文件并进行Base64编码
    with open(LOCAL_FILE_PATH, 'rb') as f:
        file_data = f.read()
    encoded_data_str = base64.b64encode(file_data).decode('ascii')

    ser = None
    try:
        ser = serial.Serial(PORT, 115200, timeout=1)
        print("1. 串口已连接。")

        # 中断并进入 Raw REPL
        print("2. 进入 Raw REPL...")
        ser.write(CTRL_C);
        time.sleep(0.1);
        ser.read_all()
        ser.write(CTRL_A);
        time.sleep(0.1);
        ser.read_all()

        # 3. 准备写入
        print(f"3. 准备写入文件 '{REMOTE_FILE_PATH}'...")
        # 导入base64模块，并以二进制写模式(wb)打开文件
        cmd = "import ubinascii; f = open('{}', 'wb')".format(REMOTE_FILE_PATH)
        success, response = execute_remote_command(ser, cmd.encode('utf-8'))
        if not success:
            print(f"  [失败] 打开远程文件失败。设备返回:\n{response.decode('utf-8', errors='ignore')}")
            return

        # 4. 分块发送Base64数据
        # 使用更小的块和更长的延时，后续有需要可以尝试略大一点的块
        chunk_size = 64
        chunks = [encoded_data_str[i:i + chunk_size] for i in range(0, len(encoded_data_str), chunk_size)]
        print(f"   文件将分为 {len(chunks)} 块传输...")

        for i, chunk in enumerate(chunks):
            print(f"   正在传输块 {i + 1}/{len(chunks)}...")
            # 构建在设备端解码并写入的命令
            cmd = "f.write(ubinascii.a2b_base64(b'{}'))".format(chunk)
            success, response = execute_remote_command(ser, cmd.encode('utf-8'))
            if not success:
                print(f"  [失败] 写入块 {i + 1} 失败。设备返回:\n{response.decode('utf-8', errors='ignore')}")
                # 尝试关闭文件以避免留下垃圾
                execute_remote_command(ser, b'f.close()')
                return
            time.sleep(0.1)  # 延时100ms

        # 5. 关闭文件
        print("   关闭远程文件...")
        success, response = execute_remote_command(ser, b'f.close()')
        if not success:
            print(f"  [失败] 关闭文件失败:\n{response.decode('utf-8', errors='ignore')}")
            return

        print("   文件传输完成。")

        # 6. 验证（看大小是否匹配）
        print("4. 正在验证文件...")
        cmd = "import os; s = os.stat('{}'); print(s[6])".format(REMOTE_FILE_PATH)
        success, response = execute_remote_command(ser, cmd.encode('utf-8'))

        if success:
            file_size_str = response.split(b'OK')[1].split(b'\r\n')[0].strip()
            remote_size = int(file_size_str)
            local_size = len(file_data)
            print(f"   [结果] 本地文件大小: {local_size} 字节, 远程文件大小: {remote_size} 字节。")
            if remote_size == local_size:
                print("   [成功] 文件大小匹配")
            else:
                print("   [失败] 文件大小不匹配")
                return
        else:
            print(f"  [失败] 验证文件失败:\n{response.decode('utf-8', errors='ignore')}")
            return

        # 7. 重新执行 main.py，相当于返回主菜单
        print("5. 正在重新执行 main.py...")
        ser.write(CTRL_B)  # 先退出 Raw REPL
        time.sleep(0.1)
        ser.write("exec(open('main.py').read())\r\n".encode('utf-8'))

        print("\n上传和验证全部成功！设备正在返回主菜单。")

    except serial.SerialException as e:
        print(f"\n错误: 串口连接失败: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("\n脚本执行完毕，串口已关闭。")


if __name__ == '__main__':
    main()
# diagnostics.py - 用于检查设备存储空间和文件系统的诊断性代码
# Diagnostic codes for checking device storage and file systems
# author: Jilin Zhou
# 2025.08.06

import serial
import time

PORT = 'COM7'  # 端口

CTRL_A = b'\x01'  # 进入 Raw REPL
CTRL_B = b'\x02'  # 退出 Raw REPL
CTRL_C = b'\x03'  # 中断
CTRL_D = b'\x04'  # 执行


def run_and_get_output(ser, command_str):
    """在设备上执行一条命令并干净地返回其打印的输出"""
    command_bytes = command_str.encode('utf-8')
    ser.write(command_bytes)
    ser.write(CTRL_D)

    response = b''
    start_time = time.time()
    while not response.endswith(b'\x04>'):
        if time.time() - start_time > 5:
            return "[错误] 命令执行超时。"
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.01)

    try:
        # 响应格式是 OK<output>\x04\x04>
        output_part = response.split(b'OK', 1)[1]
        clean_output = output_part.rsplit(b'\x04', 2)[0]
        return clean_output.strip().decode('utf-8', errors='ignore')
    except Exception:
        return f"[错误] 无法解析设备响应: {response}"


def main():
    print("--- 设备存储诊断脚本 ---")
    ser = None
    try:
        ser = serial.Serial(PORT, 115200, timeout=1)
        print(f"1. 串口已连接到 {PORT}。")

        # 中断并进入 Raw REPL
        ser.write(CTRL_C)
        time.sleep(0.1)
        ser.read_all()
        ser.write(CTRL_A)
        time.sleep(0.1)
        ser.read_all()
        print("2. 已进入 Raw REPL 模式。")

        print("\n--- 开始诊断 ---")

        # 检查1: 存储空间
        print("3. 正在检查存储空间...")
        # main.py 中使用的命令: (os.statvfs("/flash")[0]*os.statvfs("/flash")[3])
        # 可以直接运行 os.statvfs 来获取更详细的信息
        # os.statvfs('/flash') 返回: (f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax)
        # 可用空间 = f_bsize * f_bfree
        stat_cmd = "import os; s = os.statvfs('/flash'); print('{}*{}={}'.format(s[0], s[3], s[0]*s[3]))"
        output = run_and_get_output(ser, stat_cmd)

        try:
            free_space_bytes = int(output.split('=')[1])
            free_space_kb = free_space_bytes / 1024
            print(f"   [结果] 可用空间: {free_space_kb:.2f} KB")
            if free_space_kb < 10:  # 如果小于10KB，就极有可能是满了
                print("   [警告] 存储空间严重不足！可能是上传失败的原因。")
        except:
            print(f"   [错误] 无法计算空间，设备返回: {output}")

        # 检查2: 文件列表
        print("\n4. 正在列出根目录文件...")
        files_output = run_and_get_output(ser, "import os; print(os.listdir('/flash'))")
        print(f"   [结果] /flash 目录下的文件和文件夹:")
        print(f"   {files_output}")

        # 检查3: 尝试写入一个小文件
        print("\n5. 正在尝试写入一个测试文件 (test_write.txt)...")
        write_test_cmd = "with open('/flash/test_write.txt', 'w') as f: f.write('hello')"
        run_and_get_output(ser, write_test_cmd)
        size_test_cmd = "import os; print(os.stat('/flash/test_write.txt')[6])"
        size_output = run_and_get_output(ser, size_test_cmd)
        print(f"   [结果] 测试文件大小为: {size_output} 字节")
        if size_output.isdigit() and int(size_output) > 0:
            print("   [成功] 测试文件写入成功！")
            run_and_get_output(ser, "import os; os.remove('/flash/test_write.txt')")  # 清理测试文件
        else:
            print("   [失败] 测试文件写入失败！")

        print("\n--- 诊断结束 ---")

        # 退出 Raw REPL
        ser.write(CTRL_B)

    except serial.SerialException as e:
        print(f"\n错误: 串口连接失败: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("\n脚本执行完毕，串口已关闭。")


if __name__ == '__main__':
    main()
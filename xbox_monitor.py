"""
Xbox Wireless Controller 实时数据监视器
使用 Windows XInput API (xinput1_4.dll)，无需额外安装库
"""

import ctypes
import ctypes.wintypes
import time
import sys
import socket
import struct
from struct import unpack_from

LOG_FILE = r"C:\Users\35070\Desktop\xbox_log.txt"

# UDP 发送配置
ESP_IP = "192.168.4.1"   # ESP的IP地址（AP模式默认）
ESP_PORT = 8888           # ESP监听的端口
USE_UDP = True            # True=UDP, False=TCP

XINPUT_DLLS = ["xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"]

class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", ctypes.wintypes.DWORD),
        ("wButtons", ctypes.wintypes.WORD),
        ("bLeftTrigger", ctypes.c_uint8),
        ("bRightTrigger", ctypes.c_uint8),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]

BUTTON_NAMES = {
    0x0001: "D-Pad Up",
    0x0002: "D-Pad Down",
    0x0004: "D-Pad Left",
    0x0008: "D-Pad Right",
    0x0010: "Start",
    0x0020: "Back",
    0x0040: "Left Thumb",
    0x0080: "Right Thumb",
    0x0100: "LB",
    0x0200: "RB",
    0x1000: "A",
    0x2000: "B",
    0x4000: "X",
    0x8000: "Y",
}

def fmt_axis(val, fmt="{:6d}"):
    return fmt.format(val)

def main():
    xinput = None
    for dll in XINPUT_DLLS:
        try:
            xinput = ctypes.WinDLL(dll)
            break
        except OSError:
            continue

    if xinput is None:
        print("错误: 找不到 XInput DLL。请确保已安装 Xbox 手柄驱动。")
        input("按 Enter 退出...")
        return

    XInputGetState = xinput.XInputGetState
    XInputGetState.argtypes = [ctypes.wintypes.DWORD, ctypes.POINTER(XINPUT_STATE)]
    XInputGetState.restype = ctypes.wintypes.DWORD

    # 初始化 UDP socket
    udp_sock = None
    enable_udp = USE_UDP
    if enable_udp:
        try:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
            print(f"UDP 目标: {ESP_IP}:{ESP_PORT}")
        except Exception as e:
            print(f"UDP 初始化失败: {e}")
            enable_udp = False

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== Xbox 手柄数据监视器 ===\n")
        f.write(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    print("=== Xbox 手柄数据监视器 ===")
    print("按 Ctrl+C 退出\n")

    last_state = None
    ERROR_SUCCESS = 0
    ERROR_DEVICE_NOT_CONNECTED = 1167

    while True:
        state = XINPUT_STATE()
        ret = XInputGetState(0, ctypes.byref(state))

        if ret == ERROR_DEVICE_NOT_CONNECTED:
            if last_state is not None:
                msg = "[手柄已断开]"
                print(msg)
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
                last_state = None
        elif ret == ERROR_SUCCESS:
            if state.dwPacketNumber == 0 and last_state is None:
                msg = "[手柄已连接，等待数据...]"
                print(msg)
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
                last_state = state
                continue

            if last_state is None or state.dwPacketNumber != last_state.dwPacketNumber:
                ts = time.strftime("[%H:%M:%S]")
                pressed = [name for bit, name in BUTTON_NAMES.items()
                           if state.wButtons & bit]

                line = (f"{ts} 摇杆(LX={state.sThumbLX:5d} LY={state.sThumbLY:5d}) "
                        f"(RX={state.sThumbRX:5d} RY={state.sThumbRY:5d}) "
                        f"扳机(LT={state.bLeftTrigger:3d} RT={state.bRightTrigger:3d}) "
                        f"按键={pressed or '无'}")

                print(line)
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(line + "\n")

                # 通过 UDP 发送手柄数据到 ESP
                if udp_sock:
                    # 二进制打包: 按键(2B) + LT(1B) + RT(1B) + LX(2B) + LY(2B) + RX(2B) + RY(2B) = 12字节
                    pkt = struct.pack('<HBBhhhh',
                        state.wButtons,
                        state.bLeftTrigger & 0xFF,
                        state.bRightTrigger & 0xFF,
                        state.sThumbLX,
                        state.sThumbLY,
                        state.sThumbRX,
                        state.sThumbRY)
                    try:
                        udp_sock.sendto(pkt, (ESP_IP, ESP_PORT))
                    except Exception:
                        pass  # 发送失败不阻塞主循环

                last_state = state

        time.sleep(0.016)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n日志已保存至: {LOG_FILE}")
        input("按 Enter 退出...")

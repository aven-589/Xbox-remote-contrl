# Xbox-remote-contrl
使用Xbox游戏手柄来做一个自定义遥控器，不再拘束于游戏，通过wifi/蓝牙来控制可以接收蓝牙和wifi信号的设备

##你需要准备一个支持蓝牙连接的游戏手柄，分为两种，一种是经典蓝牙，另一种是BLE蓝牙，本项目适用于经典蓝牙手柄，
流程是，手柄蓝牙连接电脑，电脑监听手柄操作日志，同时电脑连接ESP32的wifi，再通过wifi把数据发给ESP32，ESP可以通过串口连接你的主控或者其他设备
再说BLE蓝牙，ESP32芯片是可以直接连接BLE蓝牙的，这样ESP32就可以直接接收游戏手柄的数据，不需要拿电脑当媒介，具体代码的话，可以直接给AI一些提示词，AI生成即可

##esp_receiver.ino，这是Arduino文件，你可以下载Arduino IDE，把代码烧录到ESP系列单片机，用于传输手柄数据

##MCU-Receiver-demo.c,这是一个stm32的hal库接收数据示例

##xbox_monitor.py，这是用于监听手柄的数据，手柄与电脑通过蓝牙连接后，终端运行该文件，会打印手柄按键日志
<img width="1481" height="761" alt="4acea73edf98b660707f8afed1468798" src="https://github.com/user-attachments/assets/0860bac0-1acb-4e34-b84b-626979c7bb12" />
<img width="1599" height="705" alt="3ddbaa214b6ccbb362606ded7288a4e7" src="https://github.com/user-attachments/assets/64555f2e-4431-465d-abef-c33825daf55e" />
<img width="1545" height="693" alt="88a65d230cddfac3da173c7bf5b351c2" src="https://github.com/user-attachments/assets/23449dee-83bb-485a-b294-3123f6fb5d1a" />
<img width="1581" height="814" alt="a562891c50d8487d8a186c1de6554c2b" src="https://github.com/user-attachments/assets/2597df7a-e580-4dc4-810f-42ee808b0309" />



#include <WiFi.h>
#include <WiFiUdp.h>

const char *ssid = "ESP_AP";
const char *password = "12345678";
const int udpPort = 8888;

WiFiUDP udp;
uint8_t buf[12];

void setup() {
  Serial.begin(921600);
  delay(100);
  Serial.println();
  Serial.println("ESP32 手柄接收端启动");

  WiFi.softAP(ssid, password);
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  udp.begin(udpPort);
  Serial.printf("UDP 监听端口: %d\n", udpPort);
  Serial.println("等待手柄数据...\n");
}

void send_serial_frame(uint8_t *data) {
  uint8_t header[] = {0xAA, 0x55};
  uint8_t footer[] = {0x0D, 0x0A};
  Serial.write(header, 2);
  Serial.write(data, 12);
  Serial.write(footer, 2);
}

void loop() {
  int len = udp.parsePacket();
  if (len >= 12) {
    udp.read(buf, 12);

    uint16_t buttons = buf[0] | (buf[1] << 8);
    uint8_t  lt = buf[2];
    uint8_t  rt = buf[3];
    int16_t  lx = buf[4] | (buf[5] << 8);
    int16_t  ly = buf[6] | (buf[7] << 8);
    int16_t  rx = buf[8] | (buf[9] << 8);
    int16_t  ry = buf[10] | (buf[11] << 8);
    send_serial_frame(buf);
  }
}

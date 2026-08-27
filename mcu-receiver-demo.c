/* USART1 帧解析状态机：AA 55 + 12字节 + 0D 0A */
#define FRAME_DATA_LEN 12

enum
{
    FRAME_WAIT_AA,
    FRAME_WAIT_55,
    FRAME_DATA,
    FRAME_WAIT_0D,
    FRAME_WAIT_0A,
};

static uint8_t frame_state = FRAME_WAIT_AA;
static uint8_t frame_buf[FRAME_DATA_LEN];
static uint8_t frame_idx = 0;
static volatile uint8_t frame_ready = 0;
static uint8_t last_frame[FRAME_DATA_LEN];

void usart1_rx_callback(uint8_t data)
{
    switch (frame_state)
    {
    case FRAME_WAIT_AA:
        if (data == 0xAA)
            frame_state = FRAME_WAIT_55;
        break;

    case FRAME_WAIT_55:
        if (data == 0x55)
        {
            frame_state = FRAME_DATA;
            frame_idx = 0;
        }
        else
        {
            frame_state = FRAME_WAIT_AA;
        }
        break;

    case FRAME_DATA:
        frame_buf[frame_idx++] = data;
        if (frame_idx >= FRAME_DATA_LEN)
        {
            frame_state = FRAME_WAIT_0D;
        }
        break;

    case FRAME_WAIT_0D:
        if (data == 0x0D)
        {
            frame_state = FRAME_WAIT_0A;
        }
        else
        {
            frame_state = FRAME_WAIT_AA;
        }
        break;

    case FRAME_WAIT_0A:
        if (data == 0x0A)
        {
            for (uint8_t i = 0; i < FRAME_DATA_LEN; i++)
            {
                last_frame[i] = frame_buf[i];
            }
            frame_ready = 1;
            esp_data.btn = last_frame[0] | (last_frame[1] << 8);  // 按钮状态
            esp_data.lt = last_frame[2];                          // 左扳机
            esp_data.rt = last_frame[3];                          // 右扳机
            esp_data.lx = last_frame[4] | (last_frame[5] << 8);   // 左摇杆X
            esp_data.ly = last_frame[6] | (last_frame[7] << 8);   // 左摇杆Y
            esp_data.rx = last_frame[8] | (last_frame[9] << 8);   // 右摇杆X
            esp_data.ry = last_frame[10] | (last_frame[11] << 8); // 右摇杆Y
        }
        frame_state = FRAME_WAIT_AA;
        break;
    }
}
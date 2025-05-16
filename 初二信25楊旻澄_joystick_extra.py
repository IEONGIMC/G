from machine import Pin, ADC, SoftI2C
import time
import framebuf

class SSD1306_I2C:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.buffer = bytearray(width * height // 8)  # 每字节存储8个像素
        self.framebuf = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MONO_HLSB)
        self.init_display()

    def init_display(self):
        # SSD1306 初始化命令序列
        init_cmds = [
            0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
            0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
            0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x30, 0xA4, 0xA6, 0xAF
        ]
        for cmd in init_cmds:
            self.i2c.writeto(self.addr, bytearray([0x00, cmd]))

    def fill(self, color):
        self.framebuf.fill(color)

    def text(self, text, x, y, color=1):
        self.framebuf.text(text, x, y, color)

    def fill_rect(self, x, y, w, h, color):
        self.framebuf.fill_rect(x, y, w, h, color)

    def blit(self, fbuf, x, y, key=0):
        self.framebuf.blit(fbuf, x, y, key)

    def show(self):
        # 分页写入数据（SSD1306要求按页传输）
        for page in range(0, self.height // 8):
            self.i2c.writeto(self.addr, bytearray([0x00, 0xB0 | page, 0x00, 0x10]))
            start = page * self.width
            end = start + self.width
            self.i2c.writeto(self.addr, b'\x40' + self.buffer[start:end])

# 摇杆引脚设置
joystick_x = ADC(Pin(33))  # X轴 (GP33)
joystick_y = ADC(Pin(32))  # Y轴 (GP32)

# LED 引脚（可选）
led_up = Pin(25, Pin.OUT)    # D1
led_down = Pin(26, Pin.OUT)  # D2
led_left = Pin(27, Pin.OUT)  # D3
led_right = Pin(4, Pin.OUT)  # D4

# OLED 初始化 (I2C)
i2c = SoftI2C(scl=Pin(14), sda=Pin(13), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# 游戏变量
player_x = 64
player_y = 32
player_size = 8
player_speed = 2
gravity = 1
player_vel_y = 0
is_jumping = False
ground_level = 56

# 平台（x, y, 宽度, 高度）
platforms = [
    (0, 60, 128, 4),  # 地面
    (20, 40, 30, 4),  # 平台1
    (70, 30, 30, 4),  # 平台2
]

# 金币（x, y）
coins = [
    (40, 20),
    (80, 10),
    (100, 50),
]

score = 0

# 玩家图像（8x8 像素）
player_img = bytearray(b'\x3C\x42\x99\xBD\xBD\x99\x42\x3C')
player_fb = framebuf.FrameBuffer(player_img, 8, 8, framebuf.MONO_HLSB)

def clear_leds():
    led_up.off()
    led_down.off()
    led_left.off()
    led_right.off()

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)

def draw_game():
    oled.fill(0)  # 清屏
    
    # 绘制平台
    for plat in platforms:
        oled.fill_rect(plat[0], plat[1], plat[2], plat[3], 1)
    
    # 绘制金币
    for coin in coins:
        oled.fill_rect(coin[0], coin[1], 4, 4, 1)
    
    # 绘制玩家
    oled.blit(player_fb, int(player_x), int(player_y), 1)
    
    # 显示分数
    oled.text(f"Score: {score}", 0, 0)
    oled.show()

def update_game():
    global player_x, player_y, player_vel_y, is_jumping, score
    
    # 读取摇杆值
    x_val = joystick_x.read()
    y_val = joystick_y.read()
    
    # 控制 LED
    clear_leds()
    if x_val < 2000:  # 左摇
        led_left.on()
        player_x -= player_speed
    elif x_val > 3000:  # 右摇
        led_right.on()
        player_x += player_speed
    
    # 跳跃控制
    if y_val < 2000 and not is_jumping:
        led_up.on()
        player_vel_y = -5
        is_jumping = True
    
    # 应用重力
    player_vel_y += gravity
    player_y += player_vel_y
    
    # 边界检查
    player_x = max(0, min(player_x, oled_width - player_size))
    player_y = max(0, min(player_y, oled_height - player_size))
    
    # 平台碰撞检测
    on_ground = False
    for plat in platforms:
        if (player_vel_y > 0 and 
            player_y + player_size >= plat[1] and 
            player_y + player_size <= plat[1] + 4 and
            player_x + player_size > plat[0] and 
            player_x < plat[0] + plat[2]):
            player_y = plat[1] - player_size
            player_vel_y = 0
            is_jumping = False
            on_ground = True
    
    # 金币收集
    for coin in coins[:]:
        if check_collision(
            int(player_x), int(player_y), player_size, player_size,
            coin[0], coin[1], 4, 4
        ):
            coins.remove(coin)
            score += 10

# 主游戏循环
while True:
    update_game()
    draw_game()
    time.sleep(0.02)
from machine import Pin, ADC
from time import sleep

# 設定 LED 腳位
led_up = Pin(25, Pin.OUT)    # D1
led_down = Pin(26, Pin.OUT)  # D2
led_left = Pin(27, Pin.OUT)  # D3
led_right = Pin(4, Pin.OUT)  # D4

# 設定搖桿的 X 和 Y 軸輸入（GP33 和 GP32）
joystick_x = ADC(Pin(33))  # 使用 GP33 作為 X 軸輸入
joystick_y = ADC(Pin(32))  # 使用 GP32 作為 Y 軸輸入

# 閾值設定
CENTER = 512   # 中心值
THRESHOLD = 150 # 靈敏度範圍（可調）

def clear_leds():
    led_up.off()
    led_down.off()
    led_left.off()
    led_right.off()

while True:
    x_val = joystick_x.read()  # 讀取 X 軸值
    y_val = joystick_y.read()  # 讀取 Y 軸值

    # 打印 X 和 Y 軸的值
    print("X:", x_val, "Y:", y_val)

    clear_leds()  # 每次 loop 先熄滅全部 LED

    # 控制 X 軸 LED
    if x_val < CENTER - THRESHOLD:
        print("LED Left ON")  # 調試信息
        led_left.on()
    elif x_val > CENTER + THRESHOLD:
        print("LED Right ON")  # 調試信息
        led_right.on()

    # 控制 Y 軸 LED
    if y_val < CENTER - THRESHOLD:
        print("LED Up ON")  # 調試信息
        led_up.on()
    elif y_val > CENTER + THRESHOLD:
        print("LED Down ON")  # 調試信息
        led_down.on()

    # 延遲一點避免太快
    sleep(0.1)
from machine import Pin, I2C
import time
import network
import socket
import gc  # Add garbage collection
from pico_i2c_lcd import I2cLcd

led = Pin("LED", Pin.OUT)

# WiFi credentials - UPDATE THESE
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

# LCD I2C configuration
LCD_I2C_NUM = 1
LCD_SCL_PIN = 11
LCD_SDA_PIN = 10
LCD_I2C_FREQ = 100000
LCD_ADDR = 0x27

# Server configuration
SERVER_PORT = 8888

# Initialize LCD
i2c = I2C(LCD_I2C_NUM, scl=Pin(LCD_SCL_PIN), sda=Pin(LCD_SDA_PIN), freq=LCD_I2C_FREQ)
lcd = I2cLcd(i2c, LCD_ADDR, 2, 16)

lcd.clear()
lcd.putstr("Connecting WiFi")

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

timeout = 20
while not wlan.isconnected() and timeout > 0:
    time.sleep(0.5)
    led.toggle()
    timeout -= 1

if not wlan.isconnected():
    lcd.clear()
    lcd.putstr("WiFi failed!")
    while True:
        time.sleep(1)

ip = wlan.ifconfig()[0]
lcd.clear()
lcd.putstr(f"IP:\n{ip}")
print(f"Pico IP: {ip}")
time.sleep(3)

# Create socket server
addr = socket.getaddrinfo('0.0.0.0', SERVER_PORT)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

lcd.clear()
lcd.putstr("Waiting for\nconnection...")

conn, addr = s.accept()
lcd.clear()
lcd.putstr("Connected!")
time.sleep(1)

# Force initial garbage collection
gc.collect()
print(f"Free memory at start: {gc.mem_free()} bytes")

frame_count = 0

# Pre-allocate buffers to avoid repeated allocation
buf = bytearray(40)
char_data = bytearray(8)

while True:
    try:
        # Force garbage collection every 50 frames
        if frame_count % 50 == 0:
            gc.collect()
            free_mem = gc.mem_free()
            print(f"Frame {frame_count}, Free memory: {free_mem} bytes")
            if free_mem < 10000:  # Warning if memory is low
                print(f"WARNING: Low memory!")
        
        # Read exactly 40 bytes over socket
        pos = 0
        while pos < 40:
            chunk = conn.recv(40 - pos)
            if not chunk:
                lcd.clear()
                lcd.putstr("Disconnected")
                led.on()
                while True:
                    time.sleep(1)
            # Copy into pre-allocated buffer
            buf[pos:pos+len(chunk)] = chunk
            pos += len(chunk)
        
        led.on()
        
        # Convert each character from column format to row format
        for char_idx in range(8):
            offset = char_idx * 5
            
            # Reuse char_data buffer instead of creating new one
            for row in range(8):
                row_byte = 0
                for col in range(5):
                    if buf[offset + col] & (1 << (7 - row)):
                        row_byte |= (1 << (4 - col))
                char_data[row] = row_byte
            
            lcd.custom_char(char_idx, bytes(char_data))
        
        # Display 8 custom characters
        lcd.move_to(0, 0)
        for i in range(4):
            lcd.putchar(chr(i))
        lcd.move_to(0, 1)
        for i in range(4, 8):
            lcd.putchar(chr(i))
        
        led.off()
        frame_count += 1

        conn.send(b'A')  # Send ACK
        
    except Exception as e:
        lcd.clear()
        lcd.putstr(f"Error F{frame_count}\n{str(e)[:16]}")
        print(f"Error at frame {frame_count}: {e}")
        led.on()
        while True:
            time.sleep(1)
import machine
import utime
import onewire
import ds18x20
import network
import socket
from machine import Pin, SPI
from ili9341 import Display, color565
from xglcd_font import XglcdFont

# Pin Definitions
LED_PIN = 16
ALARM_PIN = 17
TRIGGER_PIN = 14
ECHO_PIN = 15
CONTROL_1 = 18
CONTROL_2 = 19
DS_PIN = 22

# Setup Pins
led = machine.Pin(LED_PIN, machine.Pin.OUT)
alarm = machine.Pin(ALARM_PIN, machine.Pin.OUT)
trigger = machine.Pin(TRIGGER_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)
control_1 = machine.Pin(CONTROL_1, machine.Pin.OUT)
control_2 = machine.Pin(CONTROL_2, machine.Pin.OUT)

control_1.off()
control_2.off()

# Setup WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("BOE-", "")
#wlan.connect("Ilham", "12345678")

while not wlan.isconnected():
    print("Waiting to connect...")
    utime.sleep(1)

print("Connected to WLAN")
print("Network config:", wlan.ifconfig())

# Setup socket
ai = socket.getaddrinfo("192.168.56.127", 6002)
addr = ai[0][-1]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(False)

# Setup DS18B20 temperature sensor
ds_pin = machine.Pin(DS_PIN)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()

# Setup ILI9341 Display
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(9), cs=Pin(12), rst=Pin(13), width=240, height=320, rotation=180)

# Load fonts
arcadepix = XglcdFont('fonts/ArcadePix9x11.c', 9, 11)
broadway = XglcdFont('fonts/Broadway17x15.c', 17, 15)

def process_command(command):
    if command == "2A_ON":
        control_1.on()
        print("Control 1 turned ON")
    elif command == "2B_OFF":
        control_1.off()
        print("Control 1 turned OFF")
    elif command == "2C_ON":
        control_2.on()
        print("Control 2 turned ON")
    elif command == "2D_OFF":
        control_2.off()
        print("Control 2 turned OFF")

def get_distance():
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()
    
    while echo.value() == 0:
        pulse_start = utime.ticks_us()
    while echo.value() == 1:
        pulse_end = utime.ticks_us()
        
    pulse_duration = utime.ticks_diff(pulse_end, pulse_start)
    distance = pulse_duration * 0.0343 / 2
    return distance

# Fungsi untuk menggambar latar belakang statis
def draw_static_elements():
    display.clear(color565(0, 0, 0))  # Latar belakang hitam

    # Menambahkan Header dan IP Address
    display.draw_text(10, 10, "Monitoring Client 2", broadway, color565(255, 255, 255))
    display.draw_text(10, 40, f"IP: {wlan.ifconfig()[0]}", arcadepix, color565(200, 200, 200))

    # Garis pemisah
    display.draw_hline(10, 60, 220, color565(255, 255, 255))

    # Membuat kotak untuk setiap data dengan latar belakang warna yang lebih lembut
    display.fill_rectangle(10, 70, 220, 40, color565(0, 100, 200))  # Kotak untuk suhu
    display.fill_rectangle(10, 120, 220, 40, color565(0, 200, 100))  # Kotak untuk jarak
    display.fill_rectangle(10, 170, 220, 40, color565(200, 100, 0))  # Kotak untuk status LED
    display.fill_rectangle(10, 220, 220, 40, color565(200, 200, 0))  # Kotak untuk status alarm

    # Menambahkan tabel untuk control 1 dan control 2
    display.fill_rectangle(10, 270, 110, 40, color565(200, 0, 0))  # Kotak untuk control 1
    display.fill_rectangle(120, 270, 110, 40, color565(0, 200, 0))  # Kotak untuk control 2

    # Membuat pembatas di sekitar setiap data dan tabel
    display.draw_rectangle(10, 70, 220, 40, color565(255, 255, 255))  # Pembatas untuk suhu
    display.draw_rectangle(10, 120, 220, 40, color565(255, 255, 255))  # Pembatas untuk jarak
    display.draw_rectangle(10, 170, 220, 40, color565(255, 255, 255))  # Pembatas untuk status LED
    display.draw_rectangle(10, 220, 220, 40, color565(255, 255, 255))  # Pembatas untuk status alarm
    display.draw_rectangle(10, 270, 110, 40, color565(255, 255, 255))  # Pembatas untuk control 1
    display.draw_rectangle(120, 270, 110, 40, color565(255, 255, 255))  # Pembatas untuk control 2

# Fungsi untuk memperbarui data sensor di layar
def update_display(temperature, distance, led_status, alarm_status):
    display.draw_text(15, 80, f"Suhu: {temperature:.1f} C", arcadepix, color565(0, 0, 0),
                      background=color565(0, 100, 200))
    display.draw_text(15, 130, f"Jarak: {distance:.2f} cm", arcadepix, color565(0, 0, 0),
                      background=color565(0, 200, 100))
    display.draw_text(15, 180, f"Status Suhu: {led_status}", arcadepix, color565(0, 0, 0),
                      background=color565(200, 100, 0))
    display.draw_text(15, 230, f"Status Jarak: {alarm_status}", arcadepix, color565(0, 0, 0),
                      background=color565(200, 200, 0))
    display.draw_text(15, 280, f"Saklar 1: {'ON' if control_1.value() else 'OFF'}", arcadepix, color565(0, 0, 0),
                      background=color565(200, 0, 0))
    display.draw_text(125, 280, f"Saklar 2: {'ON' if control_2.value() else 'OFF'}", arcadepix, color565(0, 0, 0),
                      background=color565(0, 200, 0))

# Gambar elemen statis sekali
draw_static_elements()

while True:
    # Read temperature
    ds_sensor.convert_temp()
    temperature = ds_sensor.read_temp(roms[0])
    
    if temperature >= 40:
        led.on()
        led_status = "HANGAT"
    else:
        led.off()
        led_status = "NORMAL"
    
    # Measure distance
    dist = get_distance()
    print("HYSRF05 - Jarak:", dist, "cm")
    
    if dist <= 10:
        alarm.on()
        alarm_status = "DEKAT"
    else:
        alarm.off()
        alarm_status = "JAUH"

    # Print temperature readings for each sensor
    for rom in roms:
        tempC = ds_sensor.read_temp(rom)
        print('DS18B20 - temperature (ºC):', "{:.1f}".format(tempC))
    print()
    
    # Prepare sensor data to send
    sensor_data = "{:.1f}, {:.2f}, {}, {}".format(temperature, dist, led_status, alarm_status)
    s.sendto(bytes(sensor_data, "utf-8"), addr)
    
    # Tampilkan data di layar ILI9341
    update_display(temperature, dist, led_status, alarm_status)

    # Receive and process commands
    try:
        data, _ = s.recvfrom(1024)
        command = data.decode("utf-8").strip()
        process_command(command)
    except OSError:
        pass

    # Wait before repeating loop
    utime.sleep(1)




import network
import time
import socket
from machine import Pin, SPI
from bme_module import BME280Module
from ili9341 import Display, color565
from xglcd_font import XglcdFont

# Konfigurasi I2C untuk BME280
I2C_ID = 0
SCL_PIN = 1
SDA_PIN = 0

# Konfigurasi pin untuk perangkat lain
LED_PIN = 15
ALARM_PIN = 16
CONTROL_1 = 18
CONTROL_2 = 13

# Konfigurasi layar ILI9341
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(21), cs=Pin(19), rst=Pin(20),width=240, height=320, rotation=180)

# Load fonts
arcadepix = XglcdFont('fonts/ArcadePix9x11.c', 9, 11)
broadway = XglcdFont('fonts/Broadway17x15.c', 17, 15)

# Inisialisasi BME280 dan pin lainnya
bme_module = BME280Module(I2C_ID, SCL_PIN, SDA_PIN)
led = Pin(LED_PIN, Pin.OUT)
alarm = Pin(ALARM_PIN, Pin.OUT)
control_1 = Pin(CONTROL_1, Pin.OUT)
control_2 = Pin(CONTROL_2, Pin.OUT)

# Inisialisasi WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
#wlan.connect("BOE-", "")
wlan.connect("Ilham","12345678")
#wlan.connect("PUNYA GUA", "cosinusdua")

while not wlan.isconnected():
    print("Waiting to connect...")
    time.sleep(1)

ip_address = wlan.ifconfig()[0]
print(wlan.ifconfig())

# Konfigurasi socket
ai = socket.getaddrinfo("192.168.1.2", 6001)
addr = ai[0][-1]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(False)

# Fungsi untuk memproses command
def process_command(command):
    if command == "1A_ON":
        control_1.on()
        print("Control 1 turned ON")
    elif command == "1B_OFF":
        control_1.off()
        print("Control 1 turned OFF")
    elif command == "1C_ON":
        control_2.on()
        print("Control 2 turned ON")
    elif command == "1D_OFF":
        control_2.off()
        print("Control 2 turned OFF")

# Fungsi untuk menggambar latar belakang statis
def draw_static_elements():
    display.clear(color565(0, 0, 0))  # Latar belakang hitam

    # Menambahkan Header dan IP Address
    display.draw_text(10, 10, "Monitoring Client 1", broadway, color565(255, 255, 255))
    display.draw_text(10, 40, f"IP: {ip_address}", arcadepix, color565(200, 200, 200))

    # Garis pemisah
    display.draw_hline(10, 60, 220, color565(255, 255, 255))

    # Membuat kotak untuk setiap data dengan latar belakang warna yang lebih lembut
    display.fill_rectangle(10, 70, 220, 40, color565(0, 100, 200))  # Kotak untuk suhu
    display.fill_rectangle(10, 120, 220, 40, color565(0, 200, 100))  # Kotak untuk kelembaban
    display.fill_rectangle(10, 170, 220, 40, color565(200, 100, 0))  # Kotak untuk status LED
    display.fill_rectangle(10, 220, 220, 40, color565(200, 200, 0))  # Kotak untuk status alarm

    # Menambahkan tabel untuk control 1 dan control 2
    display.fill_rectangle(10, 270, 110, 40, color565(200, 0, 0))  # Kotak untuk control 1
    display.fill_rectangle(120, 270, 110, 40, color565(0, 200, 0))  # Kotak untuk control 2

    # Membuat pembatas di sekitar setiap data dan tabel
    display.draw_rectangle(10, 70, 220, 40, color565(255, 255, 255))  # Pembatas untuk suhu
    display.draw_rectangle(10, 120, 220, 40, color565(255, 255, 255))  # Pembatas untuk kelembaban
    display.draw_rectangle(10, 170, 220, 40, color565(255, 255, 255))  # Pembatas untuk status LED
    display.draw_rectangle(10, 220, 220, 40, color565(255, 255, 255))  # Pembatas untuk status alarm
    display.draw_rectangle(10, 270, 110, 40, color565(255, 255, 255))  # Pembatas untuk control 1
    display.draw_rectangle(120, 270, 110, 40, color565(255, 255, 255))  # Pembatas untuk control 2

# Fungsi untuk memperbarui data sensor di layar
def update_display(temperature, humidity, led_status, alarm_status):
    display.draw_text(15, 80, f"Suhu: {temperature} C", arcadepix, color565(0, 0, 0),
                      background=color565(0, 100, 200))
    display.draw_text(15, 130, f"Kelembapan: {humidity} %", arcadepix, color565(0, 0, 0),
                      background=color565(0, 200, 100))
    display.draw_text(15, 180, f"Suhu Ruang: {led_status}", arcadepix, color565(0, 0, 0),
                      background=color565(200, 100, 0))
    display.draw_text(15, 230, f"Kelembapan: {alarm_status}", arcadepix, color565(0, 0, 0),
                      background=color565(200, 200, 0))
    display.draw_text(15, 280, f"Saklar 1: {'ON' if control_1.value() else 'OFF'}", arcadepix, color565(0, 0, 0),
                      background=color565(200, 0, 0))
    display.draw_text(125, 280, f"Saklar 2: {'ON' if control_2.value() else 'OFF'}", arcadepix, color565(0, 0, 0),
                      background=color565(0, 200, 0))


# Gambar elemen statis sekali
draw_static_elements()

while True:
    # Pembacaan sensor
    temperature, _, humidity, _ = bme_module.get_sensor_readings()

    # Update status LED dan alarm
    if temperature >= 30:
        led.on()
        led_status = "TIDAK IDEAL"
    else:
        led.off()
        led_status = "IDEAL"

    if humidity >= 60:
        alarm.on()
        alarm_status = "TIDAK IDEAL"
    else:
        alarm.off()
        alarm_status = "IDEAL"

    # Kirim data sensor via UDP
    sensor_data = f"{temperature}, {humidity}, {led_status}, {alarm_status}"
    s.sendto(bytes(sensor_data, "utf-8"), addr)
    print(f"Sent Sensor data: {sensor_data}")

    # Tampilkan data di layar ILI9341
    update_display(temperature, humidity, led_status, alarm_status)

    # Proses command dari socket
    try:
        data, _ = s.recvfrom(1024)
        command = data.decode("utf-8").strip()
        process_command(command)
    except OSError:
        pass
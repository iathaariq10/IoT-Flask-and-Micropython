import machine
import utime
import network
import socket
from pzem import PZEM
from ili9341 import Display, color565
from xglcd_font import XglcdFont
from machine import Pin, SPI

LED_PIN = 15
ALARM_PIN = 16
CONTROL_1 = 18
CONTROL_2 = 13
HARGA_PER_KWH = 1444.70  # Harga per KWh dalam Rupiah

# Konfigurasi layar ILI9341
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(21), cs=Pin(19), rst=Pin(20),width=240, height=320, rotation=180)

# Load fonts
espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
arcadepix = XglcdFont('fonts/ArcadePix9x11.c', 9, 11)
broadway = XglcdFont('fonts/Broadway17x15.c', 17, 15)

led = machine.Pin(LED_PIN, machine.Pin.OUT)
alarm = machine.Pin(ALARM_PIN, machine.Pin.OUT)
control_1 = machine.Pin(CONTROL_1, machine.Pin.OUT)
control_2 = machine.Pin(CONTROL_2, machine.Pin.OUT)

control_1.off()
control_2.off()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
#wlan.connect("BOE-", "")
wlan.connect("Ilham","12345678")
#wlan.connect("PUNYA GUA", "cosinusdua")

while not wlan.isconnected():
    print("Menunggu koneksi...")
    utime.sleep(1)

print("Terhubung ke WLAN")
print("Konfigurasi jaringan:", wlan.ifconfig())
ip_address = wlan.ifconfig()[0]

ai = socket.getaddrinfo("192.168.1.2", 6003)
addr = ai[0][-1]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(False)

uart = machine.UART(0, baudrate=9600)
dev = PZEM(uart=uart)

dev.setAddress(0x05)
#dev.resetEnergy()

def process_command(command):
    if command == "3A_ON":
        control_1.on()
        print("Control 1 turned ON")
    elif command == "3B_OFF":
        control_1.off()
        print("Control 1 turned OFF")
    elif command == "3C_ON":
        control_2.on()
        print("Control 2 turned ON")
    elif command == "3D_OFF":
        control_2.off()
        print("Control 2 turned OFF")

def draw_static_elements():
    display.clear(color565(0, 0, 0))  # Latar belakang hitam
    display.draw_text(10, 10, "Monitoring Client 3", broadway, color565(255, 255, 255))
    display.draw_text(10, 40, f"IP: {ip_address}", arcadepix, color565(255, 255, 255))
    
    # Garis pemisah
    display.draw_hline(10, 60, 230, color565(0, 0, 255))
    display.draw_hline(10, 280, 230, color565(0, 0, 255))

    # Teks statis untuk label data
    display.draw_text(10, 70, "Arus: ", espresso_dolce, color565(255, 255, 255))
    display.draw_text(190, 70, " A", espresso_dolce, color565(255, 255, 255))
    display.draw_text(10, 105, "Voltase: ", espresso_dolce, color565(255, 255, 255))
    display.draw_text(190, 105, " V", espresso_dolce, color565(255, 255, 255))
    display.draw_text(10, 140, "Daya: ", espresso_dolce, color565(255, 255, 255))
    display.draw_text(190, 140, " W", espresso_dolce, color565(255, 255, 255))
    display.draw_text(10, 175, "Wh: ", espresso_dolce, color565(255, 255, 255))
    display.draw_text(190, 175, " Wh", espresso_dolce, color565(255, 255, 255))
    display.draw_text(10, 210, "kWh: ", espresso_dolce, color565(255, 255, 255))
    display.draw_text(180, 210, " KWh", espresso_dolce, color565(255, 255, 255))
    display.draw_text(10, 245, "Biaya: Rp ", espresso_dolce, color565(255, 255, 255))

# Gambar elemen statis sekali
draw_static_elements()

def update_data_display(arus, tegangan, daya, daya_jam, kwh, biaya):
    # Menghapus teks dinamis sebelumnya dengan menggambar ulang kotak background
    display.fill_rectangle(80, 70, 80, 30, color565(0, 0, 0))
    display.draw_text(80, 70, f"{arus:.2f}", espresso_dolce, color565(255, 255, 255))
    
    display.fill_rectangle(95, 105, 80, 30, color565(0, 0, 0))
    display.draw_text(95, 105, f"{tegangan}", espresso_dolce, color565(255, 255, 255))
    
    display.fill_rectangle(80, 140, 80, 30, color565(0, 0, 0))
    display.draw_text(80, 140, f"{daya:.2f}", espresso_dolce, color565(255, 255, 255))
    
    display.fill_rectangle(60, 175, 80, 30, color565(0, 0, 0))
    display.draw_text(60, 175, f"{daya_jam:.2f}", espresso_dolce, color565(255, 255, 255))
    
    display.fill_rectangle(60, 210, 80, 30, color565(0, 0, 0))
    display.draw_text(60, 210, f"{kwh:.3f}", espresso_dolce, color565(255, 255, 255))
    
    display.fill_rectangle(110, 245, 80, 30, color565(0, 0, 0))
    display.draw_text(110, 245, f"{biaya:.2f}", espresso_dolce, color565(255, 255, 255))

while True:
    if dev.read():
        arus = dev.getCurrent()
        tegangan = round(dev.getVoltage())
        daya = dev.getActivePower()
        daya_jam = dev.getActiveEnergy()
        
        # Hitung kWh dari daya/jam
        kwh = daya_jam / 1000
        
        # Hitung biaya berdasarkan daya/jam
        biaya = kwh * HARGA_PER_KWH
        
        print("Arus:", arus)
        print("Tegangan:", tegangan)
        print("Daya:", daya)
        print("Daya/Jam:", daya_jam)
        print("kWh:", kwh)
        print("Biaya (Rp):", biaya)
    else:
        print("Gagal membaca data sensor PZEM.")
        continue

    if arus > 0:
        led.on()
        led_status = "TERDETEKSI"
    else:
        led.off()
        led_status = "TIDAK TERDETEKSI"
    
    if tegangan >= 220:
        alarm.off()
        alarm_status = "NORMAL"
    else:
        alarm.on()
        alarm_status = "TIDAK NORMAL"

    sensor_data = "{}, {}, {}, {}, {}, {}".format(arus, tegangan, daya, daya_jam, led_status, alarm_status)
    
    s.sendto(bytes(sensor_data, "utf-8"), addr)
    
    try:
        data, _ = s.recvfrom(1024)
        command = data.decode("utf-8").strip()
        process_command(command)
    except OSError:
        pass

    # Update layar hanya pada bagian yang berubah
    update_data_display(arus, tegangan, daya, daya_jam, kwh, biaya)

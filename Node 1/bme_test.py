import utime
from machine import Pin
from bme_module import BME280Module

I2C_ID = 0
SCL_PIN = 1
SDA_PIN = 0

# Inisialisasi modul BME280
bme_module = BME280Module(I2C_ID, SCL_PIN, SDA_PIN)

while True:
    # Baca sensor
    temperature, pressure, humidity, altitude = bme_module.get_sensor_readings()

    # Format data sensor
    temperature_data = f"Temperature: {temperature} °C"
    humidity_data = f"Humidity: {humidity} %"

    # Cetak data sensor
    print(humidity_data)

    utime.sleep(60)

import time
from machine import reset, Pin
from bme_module import BME280Module

LED_PIN = 2

led = Pin(LED_PIN, Pin.OUT)
led.off()

I2C_ID = 0
SCL_PIN = 1
SDA_PIN = 0

bme_module = BME280Module(I2C_ID, SCL_PIN, SDA_PIN)

while True:
    temperature, pressure, humidity, altitude = bme_module.get_sensor_readings()

    temperature_data = f"Temperature: {temperature} °C"
    humidity_data = f"Humidity: {humidity} %"

    print(temperature_data)
    print(humidity_data)

    led.on()
    time.sleep(3)
    led.off()

    time.sleep(60)

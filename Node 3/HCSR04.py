from machine import Pin
import time

TRIG_PIN = Pin(3, Pin.OUT)  # GPIO5 for TRIG
ECHO_PIN = Pin(2, Pin.IN)   # GPIO4 for ECHO
BAUD_RATE = 9600

def setup():
    print("Ultrasonic Sensor Test")
    TRIG_PIN.off()  # Make sure TRIG is initially low
    time.sleep(2)   # Wait for sensor to settle

def get_distance():
    TRIG_PIN.on()
    time.sleep_us(10)
    TRIG_PIN.off()

    pulse_time = machine.time_pulse_us(ECHO_PIN, 1, 30000)  # Timeout after 30ms
    if pulse_time > 0:
        distance_cm = (pulse_time * 0.0343) / 2
        return distance_cm
    else:
        print("Warning: No pulse from sensor")
        return None

def loop():
    while True:
        distance = get_distance()
        if distance is not None:
            print("Distance: {:.2f} cm".format(distance))
        time.sleep(5)  # Delay between readings

setup()
loop()

import machine
import utime

# Gunakan Tegangan 5V

TRIGGER_PIN = 14
ECHO_PIN = 15

trigger = machine.Pin(TRIGGER_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)

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

try:
    while True:
        dist = get_distance()
        print("Jarak:", dist, "cm")
        utime.sleep(1)
except KeyboardInterrupt:
    print("Program berhenti oleh pengguna.")

import machine, onewire, ds18x20, time

ds_pin = machine.Pin(22)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()

while True:
  ds_sensor.convert_temp()
  time.sleep_ms(750)
  for rom in roms:
    tempC = ds_sensor.read_temp(rom)
    print('temperature (ºC):', "{:.1f}".format(tempC))
    print()
  time.sleep(120)
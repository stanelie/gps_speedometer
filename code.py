import time
import board
import busio
import neopixel
import adafruit_gps
import digitalio
import pwmio
from adafruit_motor import servo
from adafruit_simplemath import map_range

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True
# pixel_pin = board.GP16 #RP2040-zero
# num_pixels = 1
# ORDER = neopixel.GRB
# pixels = neopixel.NeoPixel(
#     pixel_pin, num_pixels, brightness=0.2, auto_write=True, pixel_order=ORDER
# )

pwm = pwmio.PWMOut(board.IO4, duty_cycle=2 ** 15, frequency=50)
speedo = servo.Servo(pwm, min_pulse=450, max_pulse=2410, actuation_range=270)

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

last_print = time.monotonic()

def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

current_value = 0
target_value = 0
while True:

    gps.update()
    if gps.speed_kmh is not None:  # Check if gps.speed_kmh has a valid value
        target_value = gps.speed_kmh
    
    if current_value < target_value:
        current_value = current_value + 0.1
    if current_value > target_value:
        current_value = current_value - 0.1
    time.sleep(0.05)
    speedo.angle = 266 - (current_value * 2.05)
#     print(current_value)
    current = time.monotonic()
    if current - last_print >= 1.0:
        time.sleep(0.1)
        last_print = current
        if not gps.has_fix:
#            print("Waiting for fix...")
#            pixels.fill((255, 0, 0))
            continue
#        if gps.satellites < 3:
#            pixels.fill((255, 0, 0))
#        if gps.satellites == 3:
#            pixels.fill((255, 255, 0))
        if gps.satellites > 3:
            led.value = False
#            pixels.fill((0, 255, 0))
#         print("Latitude: {0:.6f} degrees".format(gps.latitude))
#         print("Longitude: {0:.6f} degrees".format(gps.longitude))
        print("Speed: {} kmh".format(gps.speed_kmh))
#         print("GPS time: {}".format(_format_datetime(gps.timestamp_utc)))
#         print("# satellites: {}".format(gps.satellites))

        

import smbus
import time
import struct
import math
from neopixel import *
from weather import Weather
from threading import Timer

# Weather configuration
weather = Wea[accel, moved] = detectMovement(accel)ther()
location = weather.lookup_by_location('delft')

# NeoPixel configurations
LED_PIN        = 18      # Raspberry Pi's GPIO pin connected to the pixels
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_COUNT      = 4       # Number of LED pixels
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, 800000, 5, False, LED_BRIGHTNESS, 0, ws.WS2811_STRIP_GRB)

# Accelerometer configurations
bus = smbus.SMBus(1)
address = 0x53
gain = 3.9e-3
moveThreshold = 0.1
timeout = 7

bus.write_byte_data(address, 45, 0x00) # Go to standby mode
bus.write_byte_data(address, 44, 0x06) # Bandwidth 6.5Hz
bus.write_byte_data(address, 45, 0x08) # Go to measurement mode

def getAcceleration():
	# Read data from the sensor
	buf = bus.read_i2c_block_data(address, 50, 6)

	# Unpack the data from int16_t to python integer
	data = struct.unpack_from("<hhh", buffer(bytearray(buf)), 0)
		
	x = float(data[0]) * gain
	y = float(data[1]) * gain
	z = float(data[2]) * gain
		
	Ax = math.atan2(-x, math.sqrt(y*y + z*z)) * (180/math.pi)
	Ay = math.atan2(y, z) * (180/math.pi)
	return [x, y, z]

def mapAccelerationToColor(x, y, z):
	mag = math.sqrt(x*x + y*y + z*z)
	r = int((x/mag + 1) * (255 / 2))
	g = int((y/mag + 1) * (255 / 2))
	b = int((z/mag + 1) * (255 / 2))
	return Color(r, g, b)

def setColor(angle):
	c = mapAccelerationToColor(angle[0], angle[1], angle[2])
	for i in xrange(LED_COUNT):
		strip.setPixelColor(i, c)
	
def rain(accel):
	dir = -1
	w1 = 0
	w2 = 200
	for j in range(256):
		[accel, moved] = detectMovement(accel)
		if moved:
			return
		
		dir = dir * -1
		for i in range(200):
			w1 = w1 + dir
			w2 = w2 - dir
			c1 = Color(w1, w1, 255)
			c2 = Color(w2, w2, 255)
			c3 = c1
			c4 = c2

			strip.setPixelColor(0, c1)
			strip.setPixelColor(1, c2)
			strip.setPixelColor(2, c3)
			strip.setPixelColor(3, c4)
			strip.show()
			time.sleep(0.0001)

def sunny(accel):
	dir = -1
	green1 = 155
	green2 = 255
	for j in range(256):
		[accel, moved] = detectMovement(accel)
		if moved:
			return

		dir = dir * -1
		for i in range(100):
			green1 = green1 + dir
			green2 = green2 - dir
			c1 = Color(green1, 255, 0)
			c2 = Color(green2, 255, 0)
			c3 = c1
			c4 = c2

			strip.setPixelColor(0, c1)
			strip.setPixelColor(1, c2)
			strip.setPixelColor(2, c3)
			strip.setPixelColor(3, c4)
			strip.show()
			time.sleep(0.005)

def blinky():
	for j in range(3):
		for i in range(LED_COUNT):
			strip.setPixelColor(i, Color(255, 255, 255))
		strip.show()
		time.sleep(0.5)
		for i in range(LED_COUNT):
			strip.setPixelColor(i, Color(0, 0, 0))
		strip.show()
		time.sleep(0.5)

def weatherMode(accel):
	print "weather mode!"
	blinky()
	time.sleep(2)
 	condition = location.condition()
 	if condition.text() == 'rainy':
		rain(accel)
	elif condition.text() == 'clear':
		sunny(accel)
	
def detectMovement(prevAccel):
	accel = getAcceleration()
	dx = abs(prevAccel[0] - accel[0])
	dy = abs(prevAccel[1] - accel[1])
	dz = abs(prevAccel[2] - accel[2])
	
	if dx > moveThreshold or dy > moveThreshold or dz > moveThreshold:
		print 'moved'
		moved = True
	else:
		moved = False

	return [accel, moved]

def main():
	# Initialize the library
	strip.begin()
	
	accel = getAcceleration()

	start_time = time.time()

	while(True):
		[accel, moved] = detectMovement(accel)
		if moved:
			start_time = time.time()
		
		if (time.time()- start_time) > timeout:
			weatherMode(accel)
		
		setColor(accel)
		strip.show()
		time.sleep(0.01)

main()

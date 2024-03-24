import board
import displayio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut, Direction
import adafruit_display_text.label
import terminalio
from adafruit_bitmap_font import bitmap_font
import time
from math import sin
import ipaddress
import wifi
import socketpool
import adafruit_requests
import ssl
import re

bit_depth_value = 6
unit_width = 96
unit_height = 64
chain_width = 1
chain_height = 1
serpentine_value = True

width_value = unit_width * chain_width
height_value = unit_height * chain_height

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=width_value, height=height_value, bit_depth=bit_depth_value,
    rgb_pins=[board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    addr_pins=[board.GP10, board.GP16, board.GP18, board.GP20, board.GP22],
    clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
    tile=chain_height, serpentine=serpentine_value,
    doublebuffer=True)

DISPLAY = framebufferio.FramebufferDisplay(matrix, auto_refresh=True, rotation=180)

now = t0 = time.monotonic_ns()
append_flag = 0

class RGB_Api():

    def __init__(self):
        self.txt_color = 0x001aff
        self.txt_x = 5
        self.tram_txt_y = 20
        self.bus_txt_y = 50
        self.txt_font = terminalio.FONT
        self.txt_line_spacing = 0.8
        self.txt_scale = 2

        self.tram_label = adafruit_display_text.label.Label(
            self.txt_font,
            color=self.txt_color,
            scale=self.txt_scale,
            text="",  # Initialize as empty string
            line_spacing=self.txt_line_spacing
        )
        self.tram_label.x = self.txt_x
        self.tram_label.y = self.tram_txt_y

        self.bus_color = 0xFF0000 # Red
        self.bus_label = adafruit_display_text.label.Label(
            self.txt_font,
            color=self.bus_color,
            scale=self.txt_scale,
            text="",  # Initialize as empty string
            line_spacing=self.txt_line_spacing
        )
        self.bus_label.x = self.txt_x + 2
        self.bus_label.y = self.bus_txt_y

    def update_tram_text(self, value):
        self.tram_label.text = str(value)

    def update_bus_text(self, value):
        self.bus_label.text = str(value)

    def dynamic_text(self):
        def isTram(obj):
            return obj["transport"]["line"] == "30" and obj["transport"]["direction"] == 2

        def isBus(obj):
            return obj["transport"]["line"] != "30" and obj["transport"]["direction"] == 2
        def is_time_24h_format(input_str):
            pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
            return bool(pattern.match(input_str))

        pool = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        requests = adafruit_requests.Session(pool, ssl_context)

        while True:
            try:
                response = requests.get("http://mortvikbyalag.se/api/user/departureget")
                departurejson = response.json()
                tramdepartures = list(filter(isTram, departurejson))
                busdepartures = list(filter(isBus, departurejson))
                firsttram = str(tramdepartures[0]["time"]["displayTime"]).replace(" min", "m")
                secondtram = str(tramdepartures[1]["time"]["displayTime"]).replace(" min", "m")
                firstbus = str(busdepartures[0]["time"]["displayTime"]).replace(" min", "m")
                secondbus = str(busdepartures[1]["time"]["displayTime"]).replace(" min", "m")
                timelist = [firsttram, secondtram, firstbus, secondbus]

                for i, timeindex in enumerate(timelist):
                    if ":" in timeindex:
                        print("yes")
                        timelist[i] = ">30"

                tramstring = timelist[0] + " " + timelist[1]
                busstring = timelist[2] + " " + timelist[3]
                self.update_tram_text(tramstring)
                self.update_bus_text(busstring)




            except Exception as e:
                self.text_scale = 1
                DISPLAY.show(e)
                print("fail", e, "2")

            time.sleep(10)  # Change text every second

def connectWifi():
    #print()
    #print("Connecting to WiFi")

    wifi.radio.connect('Tele2_F182E6', 'iurvwxjp')

    #print("Connected to WiFi")

    #print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

    #print("My IP address is", wifi.radio.ipv4_address)

    ipv4 = ipaddress.ip_address("8.8.4.4")
    #print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))


if __name__ == '__main__':
    connectWifi()
    RGB = RGB_Api()
    GROUP = displayio.Group()
    GROUP.append(RGB.tram_label)
    GROUP.append(RGB.bus_label)
    DISPLAY.show(GROUP)
    RGB.dynamic_text()  # Start updating the text dynamically

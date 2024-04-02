import board
import displayio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut, Direction
import adafruit_display_text.label
import terminalio
from adafruit_bitmap_font import bitmap_font
import time
import ipaddress
import wifi
import socketpool
import adafruit_requests
import ssl
import microcontroller

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

    def update_text_size(self, value):
        self.txt_scale = value

    def dynamic_text(self):
        def isTram(obj):
            transport_info = obj.get("transport")
            if transport_info:
                line = transport_info.get("line")
                direction = transport_info.get("direction")
                if line == "30" and direction == 2:
                    return True
            return False

        def isBus(obj):
            transport_info = obj.get("transport")
            if transport_info:
                line = transport_info.get("line")
                direction = transport_info.get("direction")
                if line != "30" and direction == 2:
                    return True
            return False

        def getDepartures(requests):
            response = requests.get("http://mortvikbyalag.se/api/user/departureget")
            departurejson = response.json()
            tramdepartures = list(filter(isTram, departurejson))
            busdepartures = list(filter(isBus, departurejson))
            tramList = []
            busList = []
            i = 0
            for item in tramdepartures:
                if i < 2:
                    tramList.append(str(item["time"]["displayTime"]).replace(" min", "m"))
                    i += 1
            i = 0
            for item in busdepartures:
                if i < 2:
                    busList.append(str(item["time"]["displayTime"]).replace(" min", "m"))
                    i += 1
            tramstring = " ".join(tramList)
            busstring = " ".join(busList)
            return tramstring, busstring


        pool = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        requests = adafruit_requests.Session(pool, ssl_context)


        #i
        i = 0
        while True:
            try:
                tramstring, busstring = getDepartures(requests)
                self.txt_scale = 2
                self.update_tram_text(tramstring)
                self.update_bus_text(busstring)
                i = 0
            except Exception as e:
                self.update_text_size(1)
                upstring = e[:len(e) // 2]
                downstring = e[len(e) // 2:]
                self.update_tram_text(upstring)
                self.update_bus_text(downstring)
                print("fail", e, "2")
                if(i <= 10):
                    i += 1
                    time.sleep(2)
                    continue
                else:
                    # Restart Raspberry Pi Pico
                    print("Restarting Raspberry Pi Pico...")
                    microcontroller.reset()
            time.sleep(10)

def connectWifi():
    print("Connecting to WiFi")
    wifi.radio.connect('Tele2_F182E6', 'iurvwxjp')
    print("Connected to WiFi", wifi.radio.ipv4_address)

if __name__ == '__main__':
    connectWifi()
    RGB = RGB_Api()
    GROUP = displayio.Group()
    GROUP.append(RGB.tram_label)
    GROUP.append(RGB.bus_label)
    DISPLAY.show(GROUP)
    try:
        RGB.dynamic_text()
    except:
        microcontroller.reset()

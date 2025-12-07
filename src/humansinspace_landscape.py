import urequests
import ujson
from machine import Pin, SPI
import framebuf
import utime

# LUT tables for e-paper display
EPD_2IN9D_lut_vcomDC =[
    0x00, 0x08, 0x00, 0x00, 0x00, 0x02,
    0x60, 0x28, 0x28, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x00, 0x00, 0x00, 0x01,
    0x00, 0x12, 0x12, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00,
]
EPD_2IN9D_lut_ww =[
    0x40, 0x08, 0x00, 0x00, 0x00, 0x02,
    0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
    0x40, 0x14, 0x00, 0x00, 0x00, 0x01,
    0xA0, 0x12, 0x12, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
EPD_2IN9D_lut_bw =[
    0x40, 0x17, 0x00, 0x00, 0x00, 0x02,
    0x90, 0x0F, 0x0F, 0x00, 0x00, 0x03,
    0x40, 0x0A, 0x01, 0x00, 0x00, 0x01,
    0xA0, 0x0E, 0x0E, 0x00, 0x00, 0x02,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
EPD_2IN9D_lut_wb =[
     0x80, 0x08, 0x00, 0x00, 0x00, 0x02,
    0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
    0x80, 0x14, 0x00, 0x00, 0x00, 0x01,
    0x50, 0x12, 0x12, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
EPD_2IN9D_lut_bb =[
    0x80, 0x08, 0x00, 0x00, 0x00, 0x02,
    0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
    0x80, 0x14, 0x00, 0x00, 0x00, 0x01,
    0x50, 0x12, 0x12, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]

# Partial update LUT tables
EPD_2IN9D_lut_vcom1 =[
    0x00, 0x19, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ,0x00, 0x00,
]
EPD_2IN9D_lut_ww1 =[
    0x00, 0x19, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
EPD_2IN9D_lut_bw1 =[
    0x80, 0x19, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
EPD_2IN9D_lut_wb1 =[
    0x40, 0x19, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
EPD_2IN9D_lut_bb1 =[
    0x00, 0x19, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]

# Hardware is 128x296 (portrait), but we'll draw landscape and rotate
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

class EPD_2IN9_D_Landscape(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        # Physical dimensions
        self.hw_width = EPD_WIDTH
        self.hw_height = EPD_HEIGHT
        # Logical dimensions (landscape)
        self.width = EPD_HEIGHT  # 296
        self.height = EPD_WIDTH  # 128

        self.lut_vcomDC = EPD_2IN9D_lut_vcomDC
        self.lut_ww = EPD_2IN9D_lut_ww
        self.lut_bw = EPD_2IN9D_lut_bw
        self.lut_wb = EPD_2IN9D_lut_wb
        self.lut_bb = EPD_2IN9D_lut_bb

        self.lut_vcom1 = EPD_2IN9D_lut_vcom1
        self.lut_ww1 = EPD_2IN9D_lut_ww1
        self.lut_bw1 = EPD_2IN9D_lut_bw1
        self.lut_wb1 = EPD_2IN9D_lut_wb1
        self.lut_bb1 = EPD_2IN9D_lut_bb1

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        # Create buffer for physical display (portrait)
        self.hw_buffer = bytearray(self.hw_height * self.hw_width // 8)
        # Create landscape framebuffer
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep_ms(delaytime)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        print('e-Paper busy')
        self.send_command(0x71)
        while(self.digital_read(self.busy_pin) == 0):
            self.send_command(0x71)
        self.delay_ms(200)
        print('e-Paper busy release')

    def SetFullReg(self):
        self.send_command(0x50)
        self.send_data(0xB7)

        self.send_command(0x20)
        self.send_data1(self.lut_vcomDC[0:44])

        self.send_command(0x21)
        self.send_data1(self.lut_ww[0:42])

        self.send_command(0x22)
        self.send_data1(self.lut_bw[0:42])

        self.send_command(0x23)
        self.send_data1(self.lut_bb[0:42])

        self.send_command(0x24)
        self.send_data1(self.lut_wb[0:42])

    def SetPartReg(self):
        self.send_command(0x82)
        self.send_data(0x00)
        self.send_command(0x50)
        self.send_data(0xB7)

        self.send_command(0x20)
        self.send_data1(self.lut_vcom1[0:44])

        self.send_command(0x21)
        self.send_data1(self.lut_ww1[0:42])

        self.send_command(0x22)
        self.send_data1(self.lut_bw1[0:42])

        self.send_command(0x23)
        self.send_data1(self.lut_wb1[0:42])

        self.send_command(0x24)
        self.send_data1(self.lut_bb1[0:42])

    def TurnOnDisplay(self):
        self.send_command(0x12)
        self.delay_ms(100)
        self.ReadBusy()

    def init(self):
        print('init')
        self.reset()

        self.send_command(0x01)
        self.send_data(0x03)
        self.send_data(0x00)
        self.send_data(0x2B)
        self.send_data(0x2B)
        self.send_data(0x03)

        self.send_command(0x06)
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x17)

        self.send_command(0x04)
        self.ReadBusy()

        self.send_command(0x00)
        self.send_data(0xBF)
        self.send_data(0x0E)

        self.send_command(0x30)
        self.send_data(0x3A)

        # Send physical dimensions to hardware
        self.send_command(0x61)
        self.send_data(self.hw_width)
        self.send_data((self.hw_height&0x100)>>8)
        self.send_data(self.hw_height&0xff)

        self.send_command(0x82)
        self.send_data(0x28)

    def rotate_buffer_90(self):
        """Rotate landscape buffer 90 degrees clockwise to portrait for display"""
        # Landscape: 296x128, Portrait: 128x296
        # Create a portrait framebuffer
        portrait_fb = framebuf.FrameBuffer(self.hw_buffer, self.hw_width, self.hw_height, framebuf.MONO_HLSB)
        portrait_fb.fill(0xff)

        # Rotate each pixel from landscape to portrait
        # Landscape (x, y) -> Portrait (y, 127-x)
        for y in range(self.height):  # 0-127
            for x in range(self.width):  # 0-295
                # Get pixel from landscape buffer
                pixel = self.pixel(x, y)
                # Set in portrait buffer with 90-degree rotation
                portrait_fb.pixel(y, self.hw_height - 1 - x, pixel)

    def display(self, image):
        # Rotate landscape buffer to portrait for hardware
        self.rotate_buffer_90()

        high = self.hw_height
        wide = self.hw_width // 8
        self.send_command(0x10)
        self.send_data1([0x00] * high * wide)

        self.send_command(0x13)
        self.send_data1(self.hw_buffer)

        self.SetFullReg()
        self.TurnOnDisplay()

    def Clear(self, color):
        high = self.hw_height
        wide = self.hw_width // 8
        self.send_command(0x10)
        self.send_data1([color] * high * wide)

        self.send_command(0x13)
        self.send_data1([~color] * high * wide)

        self.SetFullReg()
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x50)
        self.send_data(0xF7)
        self.send_command(0x02)
        self.send_command(0x07)
        self.send_data(0xA5)

    def draw_huge_digit(self, digit, x, y):
        """Draw a single large digit (roughly 40x60 pixels)"""
        # Simple 7-segment-style digits using rectangles
        digits = {
            '0': [(0,0,30,8), (0,0,8,50), (22,0,8,50), (0,42,30,8)],
            '1': [(22,0,8,50)],
            '2': [(0,0,30,8), (22,0,8,25), (0,21,30,8), (0,25,8,25), (0,42,30,8)],
            '3': [(0,0,30,8), (22,0,8,25), (0,21,30,8), (22,25,8,25), (0,42,30,8)],
            '4': [(0,0,8,25), (22,0,8,50), (0,21,30,8)],
            '5': [(0,0,30,8), (0,0,8,25), (0,21,30,8), (22,25,8,25), (0,42,30,8)],
            '6': [(0,0,30,8), (0,0,8,50), (0,21,30,8), (22,25,8,25), (0,42,30,8)],
            '7': [(0,0,30,8), (22,0,8,50)],
            '8': [(0,0,30,8), (0,0,8,50), (22,0,8,50), (0,21,30,8), (0,42,30,8)],
            '9': [(0,0,30,8), (0,0,8,25), (22,0,8,50), (0,21,30,8), (0,42,30,8)],
        }

        if digit in digits:
            for rect in digits[digit]:
                self.fill_rect(x + rect[0], y + rect[1], rect[2], rect[3], 0x00)

    def draw_huge_number(self, number, center_x, y):
        """Draw a large number centered at center_x"""
        num_str = str(number)
        digit_width = 35
        total_width = len(num_str) * digit_width
        start_x = center_x - (total_width // 2)

        for i, digit in enumerate(num_str):
            self.draw_huge_digit(digit, start_x + (i * digit_width), y)

# API query function
def query_api():
    try:
        url = 'http://api.open-notify.org/astros.json'
        response = urequests.get(url)
        if response.status_code == 200:
            json_data = ujson.loads(response.text)
            print("API Response:", json_data)
            return json_data
        else:
            print("Failed to get data, status code:", response.status_code)
            return None
    except Exception as e:
        print("Error querying API:", e)
        return None

def group_by_spacecraft(people_list):
    """Group people by their spacecraft"""
    spacecraft_dict = {}
    for person in people_list:
        craft = person.get('craft', 'Unknown')
        if craft not in spacecraft_dict:
            spacecraft_dict[craft] = []
        spacecraft_dict[craft].append(person.get('name', 'Unknown'))
    return spacecraft_dict

def display_space_info():
    """Main function to display space information on e-paper in landscape"""

    # Initialize display
    epd = EPD_2IN9_D_Landscape()
    epd.Clear(0x00)

    # Get space data
    space_data = query_api()

    if space_data:
        num_people = space_data.get('number', 0)
        people_list = space_data.get('people', [])

        # Group by spacecraft
        spacecraft_groups = group_by_spacecraft(people_list)

        # Clear framebuffer (white background)
        epd.fill(0xff)

        # Layout: Left column (60px) | Center (176px) | Right column (60px)
        # Total width: 296px
        left_col_width = 60
        right_col_start = epd.width - 60

        # Draw huge number in center (centered in middle section)
        center_x = epd.width // 2
        epd.draw_huge_number(num_people, center_x, 25)

        # Draw "HUMANS IN SPACE" text below number
        epd.text("HUMANS IN SPACE", center_x - 56, 95, 0x00)

        # Draw border box around center
        center_left = left_col_width + 5
        center_right = right_col_start - 5
        epd.rect(center_left, 15, center_right - center_left, 95, 0x00)

        # Left column - spacecraft list
        left_x = 2
        y_pos = 5
        line_height = 14

        spacecraft_items = list(spacecraft_groups.items())

        # Split items between left and right
        mid_point = (len(spacecraft_items) + 1) // 2
        left_items = spacecraft_items[:mid_point]
        right_items = spacecraft_items[mid_point:]

        # Draw left column
        for craft, names in left_items:
            if y_pos > 115:
                break
            count = len(names)
            # Aggressive truncation for narrow column
            if len(craft) > 6:
                craft = craft[:5] + "."
            text = f"{craft}"
            epd.text(text, left_x, y_pos, 0x00)
            epd.text(f"({count})", left_x, y_pos + 8, 0x00)
            y_pos += line_height + 8

        # Right column - spacecraft list
        right_x = right_col_start + 2
        y_pos = 5

        for craft, names in right_items:
            if y_pos > 115:
                break
            count = len(names)
            # Aggressive truncation for narrow column
            if len(craft) > 6:
                craft = craft[:5] + "."
            text = f"{craft}"
            epd.text(text, right_x, y_pos, 0x00)
            epd.text(f"({count})", right_x, y_pos + 8, 0x00)
            y_pos += line_height + 8

        # Update display
        epd.display(epd.buffer)

    else:
        # Error display
        epd.fill(0xff)
        epd.text("Connection Error", 80, 50, 0x00)
        epd.text("Check WiFi", 95, 70, 0x00)
        epd.display(epd.buffer)

    # Sleep to save power
    epd.delay_ms(2000)
    epd.sleep()

if __name__ == "__main__":
    display_space_info()

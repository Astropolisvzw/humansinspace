import urequests
import ujson
from machine import Pin, SPI
import framebuf
import utime
import webserver

# Hardware is 128x296 (portrait), draw landscape and rotate
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

class EPD_2IN9_C_Landscape:
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

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        # Create hardware buffers (portrait)
        self.hw_buffer_black = bytearray(self.hw_height * self.hw_width // 8)
        self.hw_buffer_red = bytearray(self.hw_height * self.hw_width // 8)

        # Create landscape framebuffers for drawing
        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)

        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)

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
        print('busy')
        self.send_command(0x71)
        while(self.digital_read(self.busy_pin) == 0):
            self.send_command(0x71)
            self.delay_ms(10)
        print('busy release')

    def TurnOnDisplay(self):
        self.send_command(0x12)
        self.ReadBusy()

    def init(self):
        print('init')
        self.reset()
        self.send_command(0x06)
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_command(0x04)
        self.ReadBusy()
        self.send_command(0X00)
        self.send_data(0x8F)
        self.send_command(0X50)
        self.send_data(0x77)
        self.send_command(0x61)
        self.send_data(0x80)
        self.send_data(0x01)
        self.send_data(0x28)

    def rotate_buffer_90(self, src_fb, dst_buffer):
        """Rotate landscape buffer 90 degrees clockwise to portrait"""
        dst_fb = framebuf.FrameBuffer(dst_buffer, self.hw_width, self.hw_height, framebuf.MONO_HLSB)
        dst_fb.fill(0xff)

        for y in range(self.height):  # 0-127
            for x in range(self.width):  # 0-295
                pixel = src_fb.pixel(x, y)
                dst_fb.pixel(y, self.hw_height - 1 - x, pixel)

    def display(self):
        # Rotate both buffers
        self.rotate_buffer_90(self.imageblack, self.hw_buffer_black)
        self.rotate_buffer_90(self.imagered, self.hw_buffer_red)

        self.send_command(0x10)
        self.send_data1(self.hw_buffer_black)

        self.send_command(0x13)
        self.send_data1(self.hw_buffer_red)

        self.TurnOnDisplay()

    def Clear(self, colorblack, colorred):
        self.send_command(0x10)
        self.send_data1([colorblack] * self.hw_height * int(self.hw_width / 8))

        self.send_command(0x13)
        self.send_data1([colorred] * self.hw_height * int(self.hw_width / 8))

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0X02)
        self.ReadBusy()
        self.send_command(0X07)
        self.send_data(0xA5)
        self.delay_ms(2000)
        self.module_exit()

    def draw_huge_digit(self, framebuffer, digit, x, y):
        """Draw a single large digit on specified framebuffer"""
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
                framebuffer.fill_rect(x + rect[0], y + rect[1], rect[2], rect[3], 0x00)

    def draw_huge_number(self, framebuffer, number, center_x, y):
        """Draw a large number centered at center_x"""
        num_str = str(number)
        digit_width = 35
        total_width = len(num_str) * digit_width
        start_x = center_x - (total_width // 2)

        for i, digit in enumerate(num_str):
            self.draw_huge_digit(framebuffer, digit, start_x + (i * digit_width), y)

# API query function with retry
def query_api(retries=3):
    for attempt in range(retries):
        try:
            print(f"Querying API (attempt {attempt + 1}/{retries})...")
            url = 'http://api.open-notify.org/astros.json'
            response = urequests.get(url)
            if response.status_code == 200:
                json_data = ujson.loads(response.text)
                print("API Response:", json_data)
                return json_data
            else:
                print("Failed to get data, status code:", response.status_code)
        except Exception as e:
            print(f"Error querying API (attempt {attempt + 1}): {e}")
            if attempt < retries - 1:
                print("Retrying in 2 seconds...")
                utime.sleep(2)
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

def format_timestamp():
    """Format current time as HH:MM"""
    t = utime.localtime()
    return "{:02d}:{:02d}".format(t[3], t[4])

def display_space_info(web_server=None):
    """Main function to display space information with RED number"""

    # Initialize display
    epd = EPD_2IN9_C_Landscape()
    epd.Clear(0xff, 0xff)

    # Get space data
    space_data = query_api()
    timestamp = format_timestamp()

    # Update web server data if provided
    if web_server and space_data:
        web_server.set_data(space_data, timestamp)

    if space_data:
        num_people = space_data.get('number', 0)
        people_list = space_data.get('people', [])

        # Group by spacecraft
        spacecraft_groups = group_by_spacecraft(people_list)

        # Clear framebuffers (white background)
        epd.imageblack.fill(0xff)
        epd.imagered.fill(0xff)

        # Center everything for cleaner look
        center_x = epd.width // 2

        # Spacecraft list at the top - centered horizontally, can wrap to multiple lines
        spacecraft_items = list(spacecraft_groups.items())
        spacecraft_text = "  ".join([f"{craft} ({len(names)})" for craft, names in spacecraft_items])

        # Simple word wrapping for spacecraft list
        spacecraft_start_y = 5
        y_pos = spacecraft_start_y
        line_height = 10
        max_width = 35  # characters per line
        words = spacecraft_text.split()
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) <= max_width:
                current_line = test_line
            else:
                # Draw current line centered
                text_width = len(current_line) * 8
                x_pos = center_x - text_width // 2
                epd.imageblack.text(current_line, x_pos, y_pos, 0x00)
                y_pos += line_height
                current_line = word

        # Draw last line
        if current_line:
            text_width = len(current_line) * 8
            x_pos = center_x - text_width // 2
            epd.imageblack.text(current_line, x_pos, y_pos, 0x00)
            y_pos += line_height

        spacecraft_end_y = y_pos

        # Multilingual text at the bottom (fixed position)
        text_block_height = 30  # 3 lines * 10px
        bottom_text_y = epd.height - text_block_height - 3

        epd.imageblack.text("Mensen in de ruimte", center_x - 76, bottom_text_y, 0x00)
        epd.imageblack.text("Humans in Space", center_x - 60, bottom_text_y + 10, 0x00)
        epd.imageblack.text("Gens dans l'espace", center_x - 72, bottom_text_y + 20, 0x00)

        # Calculate vertical center between spacecraft and bottom text
        number_height = 50  # approximate height of the big number
        available_space = bottom_text_y - spacecraft_end_y
        number_y = spacecraft_end_y + (available_space - number_height) // 2

        # Draw huge RED number in vertical center
        epd.draw_huge_number(epd.imagered, num_people, center_x, number_y)

        # Update display
        epd.display()

    else:
        # Error display
        epd.imageblack.fill(0xff)
        epd.imagered.fill(0xff)
        epd.imagered.text("Connection Error", 80, 50, 0x00)
        epd.imageblack.text("Check WiFi", 95, 70, 0x00)
        epd.display()

    # Sleep to save power
    epd.delay_ms(2000)
    epd.sleep()

if __name__ == "__main__":
    display_space_info()

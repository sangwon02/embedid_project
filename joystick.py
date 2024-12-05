import board
from digitalio import DigitalInOut, Direction
from adafruit_rgb_display import st7789

# 조이스틱 및 디스플레이 설정
class Joystick:
    def __init__(self):
        self.cs_pin = DigitalInOut(board.CE0)
        self.dc_pin = DigitalInOut(board.D25)
        self.reset_pin = DigitalInOut(board.D24)
        self.BAUDRATE = 24000000

        self.spi = board.SPI()
        self.disp = st7789.ST7789(
            self.spi,
            height=240,
            y_offset=80,
            rotation=180,
            cs=self.cs_pin,
            dc=self.dc_pin,
            rst=self.reset_pin,
            baudrate=self.BAUDRATE,
        )

        # Input pins
        self.button_A = DigitalInOut(board.D5) 
        self.button_A.direction = Direction.INPUT

        self.button_B = DigitalInOut(board.D6) 
        self.button_B.direction = Direction.INPUT

        self.button_L = DigitalInOut(board.D27)
        self.button_L.direction = Direction.INPUT

        self.button_R = DigitalInOut(board.D23)
        self.button_R.direction = Direction.INPUT

        self.button_U = DigitalInOut(board.D17)
        self.button_U.direction = Direction.INPUT

        self.button_D = DigitalInOut(board.D22)
        self.button_D.direction = Direction.INPUT

        # Turn on the Backlight
        self.backlight = DigitalInOut(board.D26)
        self.backlight.switch_to_output()
        self.backlight.value = True

        self.width = self.disp.width
        self.height = self.disp.height

    def get_command(self):
        commands = []
        if not self.button_U.value:
            commands.append('up_pressed')
        if not self.button_D.value:
            commands.append('down_pressed')
        if not self.button_L.value:
            commands.append('left_pressed')
        if not self.button_R.value:
            commands.append('right_pressed')
        if not self.button_A.value:
            commands.append('a_pressed')
        if not self.button_B.value:
            commands.append('b_pressed')
        return commands if commands else None
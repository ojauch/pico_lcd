from machine import Pin
import utime

class Display:

    CMD_MODE = 0
    DATA_MODE = 1

    LCD_BOOTUP_TIME = 0.015
    LCD_ENABLE_TIME = 0.00002
    LCD_WRITEDATA_TIME = 0.00046
    LCD_COMMAND_TIME = 0.00042
    LCD_SOFT_RESET_TIME1 = 0.005
    LCD_SOFT_RESET_TIME2 = 0.001
    LCD_SOFT_RESET_TIME3 = 0.001
    LCD_SET_4BITMODE_TIME = 0.005
    LCD_CLEAR_DISPLAY_TIME = 0.002
    LCD_CURSOR_HOME_TIME = 0.002

    LCD_CLEAR_CMD = 0x01
    LCD_CURSOR_HOME_CMD = 0x02
    LCD_SOFT_RESET_CMD = 0x30

    LCD_SET_FUNCTION = 0X20
    LCD_FUNCTION_4BIT = 0x00
    LCD_FUNCTION_2LINE = 0x08
    LCD_FUNCTION_5X7 = 0x00

    LCD_SET_DISPLAY = 0x08
    LCD_DISPLAY_OFF = 0x00
    LCD_DISPLAY_ON = 0x04
    LCD_CURSOR_OFF = 0x00
    LCD_CURSOR_ON = 0x02
    LCD_BLINKING_OFF = 0x00
    LCD_BLINKING_ON = 0x01
    
    def __init__(self, enable_pin, register_pin,
                 data4_pin, data5_pin, data6_pin, data7_pin):
        self.enable_pin = Pin(enable_pin, Pin.OUT)
        self.register_pin = Pin(register_pin, Pin.OUT)
        self.data4_pin = Pin(data4_pin, Pin.OUT)
        self.data5_pin = Pin(data5_pin, Pin.OUT)
        self.data6_pin = Pin(data6_pin, Pin.OUT)
        self.data7_pin = Pin(data7_pin, Pin.OUT)
        
        # init display
        utime.sleep(self.LCD_BOOTUP_TIME)

        # send 3 soft reset commands
        self.set_mode(self.CMD_MODE)
        self.send_half_byte(self.LCD_SOFT_RESET_CMD >> 4)
        utime.sleep(self.LCD_SOFT_RESET_TIME1)
        self.enable()
        utime.sleep(self.LCD_SOFT_RESET_TIME2)
        self.enable()
        utime.sleep(self.LCD_SOFT_RESET_TIME3)

        # activate 4 bit mode
        self.send_half_byte((self.LCD_SET_FUNCTION | self.LCD_FUNCTION_4BIT) >> 4)
        utime.sleep(self.LCD_SET_4BITMODE_TIME)

        # 4 bit / 2 line / 5x7
        self.send_command((self.LCD_SET_FUNCTION | self.LCD_FUNCTION_4BIT | self.LCD_FUNCTION_2LINE | self.LCD_FUNCTION_5X7))

        # display on / cursor off / blinking off
        self.send_command((self.LCD_SET_DISPLAY | self.LCD_DISPLAY_ON | self.LCD_CURSOR_OFF | self.LCD_BLINKING_OFF))

        self.clear_screen()
        self.return_cursor()

    def enable(self):
        self.enable_pin.value(1)
        utime.sleep(self.LCD_ENABLE_TIME)
        self.enable_pin.value(0)
        utime.sleep(self.LCD_ENABLE_TIME)
    

    def send_byte(self, byte, mode):
        # set command or data mode pin
        self.register_pin.value(mode)
        
        # split byte in two halfs
        upper_half = (byte & 0xF0) >> 4
        lower_half = byte & 0x0F
        
        self.send_half_byte(upper_half)
        self.send_half_byte(lower_half)
        
        if mode:
            utime.sleep(self.LCD_WRITEDATA_TIME)
        else:
            utime.sleep(self.LCD_COMMAND_TIME)


    def send_half_byte(self, data):
        if data & 0x8:
            self.data7_pin.value(1)
        else:
            self.data7_pin.value(0)
        
        if data & 0x4:
            self.data6_pin.value(1)
        else:
            self.data6_pin.value(0)
        
        if data & 0x2:
            self.data5_pin.value(1)
        else:
            self.data5_pin.value(0)
        
        if data & 0x1:
            self.data4_pin.value(1)
        else:
            self.data4_pin.value(0)
        
        self.enable()


    def set_mode(self, mode):
        self.register_pin.value(mode)


    def clear_screen(self):
        self.send_byte(self.LCD_CLEAR_CMD, self.CMD_MODE)
        utime.sleep(self.LCD_CLEAR_DISPLAY_TIME)


    def return_cursor(self):
        self.send_byte(self.LCD_CURSOR_HOME_CMD, self.CMD_MODE)
        utime.sleep(self.LCD_CURSOR_HOME_TIME)


    def send_char(self, char):
        self.send_byte(char, self.DATA_MODE)
        utime.sleep(self.LCD_WRITEDATA_TIME)
        

    def send_command(self, byte):
        self.send_byte(byte, self.CMD_MODE)
        utime.sleep(self.LCD_COMMAND_TIME)


    def str_to_bytes(self, string):
        str_bytes = [elem.encode("hex") for elem in string]
        return str_bytes


    def print_message(self, message):
        self.clear_screen()
        self.return_cursor()
        
        message_bytes = self.str_to_bytes(message)
        for char in message_bytes:
            self.send_char(ord(char))
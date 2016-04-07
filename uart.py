import pyserial

class Usart:
    def __init___(self, serial_port, baudrate):
        self.uart = serial.Serial(serial_port, baudrate)

    def readline(self):
        self.uart.readline()

usart = Usart("COM4", 57600)
file = open("data", "a")

while True:
    try:
        rawline = usart.readline()
        line = rawline.decode('utf-8')
    except UnicodeDecodeError:
        print(rawline)
        print("line cannot be decoded\n")
        continue
    file.write(line)
    file.flush()

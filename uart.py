import serial

import uart_config


class Usart:
    def __init__(self, serial_port, baudrate):
        self.uart = serial.Serial(serial_port, baudrate)

    def readline(self):
        return self.uart.readline()

if __name__ == '__main__':
    usart = Usart(uart_config.device, uart_config.baudrate)
    file = open(uart_config.filename, "a")
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

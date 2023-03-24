import serial
import time
class LoRa:
    def __init__(self):
        self.serial = serial.Serial(
            port = '/dev/ttyAMA0',
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )            
    
    def cmd(self, lora_cmd):
        self.serial.write(('{}\r\n'.format(lora_cmd)).encode())
        time.sleep(1)
        reply = self.serial.readline().decode()
        print(reply.strip('\r\n'))
	#print(reply.decode().strip('\r\n'))
    def test(self):
        self.cmd('AT')

    def set_addr(self, addr):
        self.cmd('AT+ADDRESS={}'.format(addr))
        self.cmd('AT+ADDRESS?')


    def send_msg(self, addr, msg):
        self.cmd('AT+SEND={},{},{}'.format(addr,len(msg),msg))

    def read_msg(self):
        msg = self.serial.readline().decode()
        if msg!='':
            rcv = msg.removeprefix("+RCV=").strip('\r\n').split(",")
            received_dict = {'sender': rcv[0], 'length': rcv[1], 'rssi': rcv[-2], 'snr': rcv[-1], 'filename': rcv[2], 'data': ','.join(rcv[3:-2]) }

            return received_dict

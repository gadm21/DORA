import serial
from time import sleep


class ReliableLoRa:
    def __init__(self):
        self.serial = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )            
        self.parameters = {'SF': 10, 'BW': 7, 'CR': 1, 'PP': 7}
        
    def cmd(self, lora_cmd):
        self.serial.write(('{}\r\n'.format(lora_cmd)).encode())
        return self.serial.readline().decode()

    def test(self):
        self.cmd('AT')

    def set_addr(self, addr):
        self.cmd('AT+ADDRESS={}'.format(addr))
        return self.cmd('AT+ADDRESS?')

    def set_param(self, parameter, value): 
        assert parameter in self.parameters.keys()  # Spreading Factor, Bandwidth, Coding Rate, Programmed Preamble
        if self.parameters[parameter] == value:
            return 
        self.parameters[parameter] = value
        command = 'AT+PARAMETER=' + ','.join(str(self.parameters.values()))
        self.cmd(command) 
    
    def wait(self):
        self.serial.readline()
        
    def send_msg(self, addr, msg):
        return self.cmd('AT+SEND={},{},{}'.format(addr,len(msg),msg))

    def read_msg(self):
        msg = list()
        while self.serial.in_waiting:
            msg += self.serial.readlines()
        if not msg:
            return list()
        msg = [line.decode() for line in msg]
        # print(msg)
        # identify packets
        start_indices = [i for i, line in enumerate(msg) if '+RCV' in line]
        end_indices = [i for i, line in enumerate(msg) if 'EOP' in line]
        packet_start_end = list()
        for i in start_indices:
            for j in end_indices:
                if i < j:
                    packet_start_end.append((i, j))
                    break
        # get packets from received lines
        packets = []
        for (i, j) in packet_start_end:
            packets.append(''.join(line for line in msg[i:j]))
        
        # decapsulate packets
        decap_packets = []
        for packet in set(packets):
            fields = packet.split('\r\n')
            header = fields[0].split(',')
            decap_packets.append(header[0] + '\r\n' + header[-1] + '\r\n' + fields[1])
        decap_packets.sort(key=lambda x: int(x.split('\r\n')[1]))
        return decap_packets


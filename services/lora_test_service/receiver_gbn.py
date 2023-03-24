import LoRa
from math import inf
from time import time
from sys import argv
import serial






class LoRa:
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
        f = lambda x, y: x in y
        start_indices = [i for i, line in enumerate(msg) if f('+RCV', line)]
        end_indices = [i for i, line in enumerate(msg) if f('EOP', line)]
        
        # get packets from received lines
        packets = []
        if len(start_indices) > 0:
            for i in start_indices:
                if len(end_indices) == 0:
                    break
                end_found_flag = False
                for index, j in enumerate(end_indices):
                    if j > i:
                        packets.append(''.join(line for line in msg[i:j]))
                        end_found_flag = True
                        break    
                if end_found_flag:
                    del end_indices[index]
        
        # decapsulate packets
        decap_packets = []
        for packet in set(packets):
            fields = packet.split('\r\n')
            decap_packets.append(fields[0].split(',')[-1] + '\r\n' + fields[1])
        decap_packets.sort(key = lambda x: int(x.split('\r\n')[0]))
        return decap_packets

def get_time(as_str = False) :
    datetime_components = ['month', 'day', 'hour', 'minute', 'ampm', 'year']
        
    time_value = {name : value for (name, value) in zip( datetime_components, datetime.datetime.now().strftime('%b-%d-%I-%M-%p-%G').split('-'))}
    for key in time_value.keys() :
        try :
            time_value[key] = int(time_value[key])
        except :
            pass
        
    if as_str : 

        time_value = ' '.join([ key + '_' + str(value) for (key, value) in time_value.items()]) 

    return time_value


def rcv_msg(receiverSocket: LoRa, timeout):
    start_time = time()
    while time() - start_time < timeout:
        packets = receiverSocket.read_msg()
        if packets:
            break
        else:
            continue
    return packets


def format_ack(ack_num):
    return f"1\r\n{ack_num}\r\nEOP"


lora = LoRa.LoRa()  # Initialize serial instance
lora.set_addr(2)  # Sets the LoRa address
sender_address = 1
data_dir = '/home/pi/Desktop/reciever/'

# protocol params
# timeout = argv[1]
timeout = 4
max_time = 12_000
print(f"Receiver Timeout: {timeout}")

num_packets = inf
received_data = ''
num_received_packets = 0
next_packet_num = 0

start_time = time()
f = open(data_dir + 'receiver_log.txt', 'w')
while num_received_packets < num_packets:
    if time() - start_time > max_time:
        f.write(f"Receiver timed out after {max_time} ms")
        exit()
    print(f"Expected Packet: {next_packet_num}")
    packets = rcv_msg(lora, timeout)
    try: 
        f.write(f"Received Packets: {packets}\n")
        f.write(get_time(as_str = True))
        f.write('\n')
    except:
        pass 

    for packet in packets:
        packet_num, data = packet.split("\r\n")
        packet_num = int(packet_num)
        if packet_num == next_packet_num:
            if packet_num == 0 and num_packets == inf:
                num_packets = int(data)
                num_received_packets += 1
                next_packet_num = packet_num + 1
            else:
                received_data += data
                num_received_packets += 1
                next_packet_num = packet_num + 1
    ack = format_ack(str(next_packet_num))
    lora.send_msg(sender_address, str(len(ack)) + ',' + ack)
    lora.wait()

ack = format_ack(str(next_packet_num))
for i in range(5):
    lora.send_msg(sender_address, str(len(ack)) + ',' + ack)
    lora.wait()


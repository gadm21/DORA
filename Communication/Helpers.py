from GlobalVariables import *
import ReliableLoRa
from time import time
all_data = {}

def save_data(data_dir,filename):
    global all_data
    data = all_data[filename]
    with open(data_dir+filename, 'a') as f:
        num_lines = len(data) 
        for datum in data :
            f.write(datum+'\n')
        print("file {} has {} lines".format(filename, num_lines))

def prepare_data(raw_data, segment_size):
    raw_data = str(raw_data)
    num_packets = len(raw_data) // segment_size + 1
    return [(str(i+2) + '\r\n' + raw_data[i * segment_size:] + '\r\nEOP') if i == num_packets - 1 else
            (str(i+2) + '\r\n' + raw_data[i * segment_size:(i + 1) * segment_size] + '\r\nEOP')
            for i in range(num_packets)]


def rcv_ack(next_packet_num, sender_socket: ReliableLoRa, timeout, last_ack_num):
    ack_num_list = [last_ack_num, ]
    start_time = time()
    while (time() - start_time < timeout) and (max(ack_num_list) == last_ack_num):
        packets = sender_socket.read_msg()
        if packets:
            ack_num_list = [i for i in [int(packet.split('\r\n')[-1]) for packet in packets]]
            break
        else:
            continue
    return max(ack_num_list)

def rcv_msg(receiver_socket: ReliableLoRa, timeout):
    packets = list()
    start_time = time()
    while time() - start_time < timeout:
        packets = receiver_socket.read_msg()
        if packets:
            break
        else:
            continue
    return packets


def format_ack(ack_num):
    return f"1\r\n{ack_num}\r\nEOP"

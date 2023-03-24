import LoRa
from time import time


def prepare_data(raw_data, segment_size):
    num_packets = len(raw_data) // segment_size + 1
    return [(str(i+1) + '\r\n' + raw_data[i * segment_size:] + '\r\nEOP') if i == num_packets - 1 else
            (str(i+1) + '\r\n' + raw_data[i * segment_size:(i + 1) * segment_size] + '\r\nEOP')
            for i in range(num_packets)]


def rcv_ack(next_packet_num, senderSocket: LoRa, timeout, last_ack_num):
    ack_num = last_ack_num
    start_time = time()
    ack_num_list = [] 
    while (time() - start_time < timeout) and (last_ack_num == ack_num):
        packets = senderSocket.read_msg()
        if packets:
            ack_num_list = [int(packet.split('\r\n')[-1]) for packet in packets]
            ack_num_list = [i for i in ack_num_list if i<= next_packet_num]
            break
        else:
            continue
    return max(ack_num_list) if len(ack_num_list) > 0 else last_ack_num

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

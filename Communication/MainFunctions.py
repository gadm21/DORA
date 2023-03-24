from GlobalVariables import *
from Helpers import *
import LoRa
import ReliableLoRa
import time
from pathlib import Path
from math import inf

def send_txt(file_path, receiver_id, delay=default_delay):
    lora = LoRa.LoRa() # Initialize serial instance
    #time.sleep(3)
    lora.set_addr(raspberry_id)  # Sets the LoRa address
    receiver_addr = receiver_id
    filename = Path(file_path).name

    with open(file_path) as f:
        for line in f:
            print("sending data", line.strip('\r\n'))
            lora.send_msg(receiver_addr, filename+','+line.strip('\r\n'))
            time.sleep(delay)
        print("Done sending file")
    
def receive_txt(data_dir):  
    lora = LoRa.LoRa() # Initialize serial instance
    lora.set_addr(raspberry_id)  # Sets the LoRa address
    
    count = 0
    data_maxlen = default_data_maxlen 
    idle_maxwait = default_idle_maxwait # seconds
    last_received_at = time.time()
    global all_data
           
    while 1:
            received = lora.read_msg()
            waiting_time = time.time() - last_received_at
            if bool(received):
                last_received_at = time.time() 
                datum = received['data']
                filename = received['sender']+'_'+received['filename'] #125_test.txt >> from sender 125
                print('received:', datum)
                if not filename in all_data.keys() :
                    all_data[filename] = []
                all_data[filename].append(datum)
                if len(all_data[filename]) > data_maxlen:
                    save_data(filename)
                    all_data[filename] = []
            elif waiting_time > idle_maxwait :
                for filename, data in all_data.items() :
                    if len(data) > 0 :
                        save_data(data_dir,filename)
                        all_data[filename]= []
                        

def send_reliable(file_path, receiver_id,
                  window_size=default_window_size,
                  segment_size=default_segment_size,
                  timeout=default_timeout,
                  max_time=default_max_time):
    lora = ReliableLoRa.ReliableLoRa()  # Initialize serial instance
    lora.set_addr(raspberry_id)  # Sets the LoRa address
    receiver_address = receiver_id

    # print(f"window size: {window_size}, sender timeout: {timeout}")
    # prepare the packets
    f = open(file_path, 'rb')
    filename = f.name.split('/')[-1]
    data = f.read()
    data_packets = prepare_data(data, segment_size)
    num_packets = len(data_packets) + 2
    all_packets = [('0\r\n' + str(num_packets) + '\r\nEOP'), ('1\r\n' + filename + '\r\nEOP')]
    all_packets.extend(data_packets)

    # start sending
    start_time = time.time()
    next_packet_num = 0
    while next_packet_num < num_packets:
        if time.time() - start_time > max_time:
            exit()
        packets_to_send = all_packets[next_packet_num:next_packet_num + window_size]
        for packet in packets_to_send:
            lora.send_msg(receiver_address, str(len(packet)) + ',' + packet)
            lora.wait()
        ack_num = rcv_ack(next_packet_num + window_size, lora, timeout, next_packet_num)
        print("Current ACK: " + str(ack_num))
        next_packet_num = ack_num

                
def receive_reliable(data_dir,
                     timeout=default_receiver_timeout,
                     max_time=default_receiver_max_time):
    lora = ReliableLoRa.ReliableLoRa()  # Initialize serial instance
    lora.set_addr(raspberry_id)  # Sets the LoRa address
    # protocol params
    # timeout = argv[1]
    print(f"Receiver Timeout: {timeout}")
    filename = None
    sender_address = -1
    num_packets = inf
    received_data = ''
    num_received_packets = 0
    next_packet_num = 0
    start_time = time.time()
    while num_received_packets < num_packets:
        if time.time() - start_time > max_time:
            exit()
        print(f"Expected Packet: {next_packet_num}")
        packets = rcv_msg(lora, timeout)
        print(packets)

        for packet in packets:
            curr_sender_address, packet_num, data = packet.split("\r\n")
            packet_num = int(packet_num)
            if packet_num == next_packet_num:
                if packet_num == 0 and num_packets == inf:
                    sender_address = curr_sender_address
                    num_packets = int(data)
                    num_received_packets += 1
                    next_packet_num = packet_num + 1
                elif curr_sender_address == sender_address:
                    if packet_num == 1:
                        filename = data
                        num_received_packets += 1
                        next_packet_num = packet_num + 1
                    else:
                        received_data += data
                        num_received_packets += 1
                        next_packet_num = packet_num + 1
        if next_packet_num != 0:
            ack = format_ack(str(next_packet_num))
            lora.send_msg(sender_address, str(len(ack)) + ',' + ack)
            lora.wait()

    ack = format_ack(str(next_packet_num))
    for i in range(5):
        lora.send_msg(sender_address, str(len(ack)) + ',' + ack)
        lora.wait()

    if filename:
        with open(data_dir + filename, 'a') as f:
            f.write(received_data)
        f.close()


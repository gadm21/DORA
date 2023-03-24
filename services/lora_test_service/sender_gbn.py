import LoRa
from HelperFunctions import *
from sys import argv


lora = LoRa.LoRa()  # Initialize serial instance
lora.set_addr(1)  # Sets the LoRa address
receiver_address = 2
# data_dir = '/home/pi/Desktop/Data/'
data_dir = '/home/pi/Desktop/sender/'
test_file = 'test_file.txt'
filename = data_dir + test_file

# protocol parameters
window_size = int(argv[1])
segment_size = 20 # 7-bit characters - 224 Bytes Segment
timeout = int(argv[2])
max_time = 500

# print(f"window size: {window_size}, sender timeout: {timeout}")
# prepare the packets
f = open(filename)
print("file name:", filename) 
data = f.read()
data_packets = prepare_data(data, segment_size)
num_packets = len(data_packets) + 1
all_packets = [('0\r\n' + str(num_packets) + '\r\nEOP'), ]
all_packets.extend(data_packets)
print("num packets:", num_packets)
for p in data_packets :
    print("packet:", p) 
# start sending
start_time = time()
next_packet_num = 0
while next_packet_num < num_packets:
    if time() - start_time > max_time:
        f2 = open(data_dir + 'results.txt', 'a')
        f2.write(f"window size: {window_size}, sender timeout: {timeout}, timedout\n")
        f2.close()
        exit()
    packets_to_send = all_packets[next_packet_num:next_packet_num + window_size]
    for packet in packets_to_send:
        lora.send_msg(receiver_address, str(len(packet)) + ',' + packet)
        lora.wait()
    ack_num = rcv_ack(next_packet_num + window_size, lora, timeout, next_packet_num)
    print("Current ACK: " + str(ack_num))
    next_packet_num = ack_num 
end_time = time() 

# save the results to a file
print("writing to file") 
f2 = open(data_dir + 'results.txt', 'a')
f2.write(f"window size: {window_size}, sender timeout: {timeout}, time: {end_time - start_time}\n")
f2.close()





from LoRaCommunication import *

file_path = '/home/pi/Desktop/Data/test.txt'

#Examples for unreliable send 
send_file(file_path)
# 
# send_file(file_path, receiver_id= 124,params={'delay': 4})
# 
# #Examples for reliable send 
# send_file(file_path,reliable=True)
# 
# send_file(file_path, receiver_id= 124, reliable=True, {'window_size' : 3,
#                                                        'segment_size' : 20,
#                                                        'timeout' : 3,
#                                                        'max_time' : 1500})


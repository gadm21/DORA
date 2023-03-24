from MainFunctions import *
import os

#For unreliable, default params={'delay': 3} 
#For reliable, default params={window_size : 3,
                              #segment_size : 20,
                              #timeout : 3,
                              #max_time : 1500}
def send_file(file_path, receiver_id= default_receiver_id,reliable=False, params={}):
    if reliable:
        send_reliable(file_path, receiver_id, **params)
    else:
        send_txt(file_path, receiver_id, **params)
    
def receive_file(data_dir=default_data_dir, reliable=False, params={}):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if reliable:
        receive_reliable(data_dir, **params) #default params= {receiver_timeout : 4, receiver_max_time : 1200}
    else:
        receive_txt(data_dir)
    

            
        

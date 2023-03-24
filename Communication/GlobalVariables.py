from os import environ
raspberry_id = int(environ.get('raspberry_id'))
default_receiver_id = 104
default_data_dir = '/home/pi/Desktop/Data/Received/'

# default params for unreliable communication
default_delay = 3
default_data_maxlen = 99 
default_idle_maxwait = 5  # seconds

# default params for reliable communication
# sender
default_window_size = 1
default_segment_size = 20  # 7-bit characters - 224 Bytes Segment
default_timeout = 4
default_max_time = 1500
# receiver
default_receiver_timeout = 4
default_receiver_max_time = 1200

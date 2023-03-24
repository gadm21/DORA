import os
import json
from time import time
from collections import defaultdict
from itertools import product


try:
    f = open('rate_dict.json', 'r')
    rate_dict = json.load(f)
    f.close()
except FileNotFoundError:
    nested_dict = lambda: defaultdict(nested_dict)
    rate_dict = nested_dict()

file_size = 12.8 # Kb
sender_timeout_vals = range(3, 10 + 1)
window_size_vals = range(1, 10 + 1)
receiver_timeout = 4


for sender_timeout, window_size in product(sender_timeout_vals, window_size_vals):
    # run sender with params
    start_time = time()
    os.system(f"python sender_gbn.py {window_size} {sender_timeout}")
    end_time = time()
    data_rate = round(file_size/(end_time-start_time), 10)
    print(f"Window Size: {window_size}, Sender Timeout: {sender_timeout}, Receiver Timeout: {receiver_timeout} ----> Data Rate: {data_rate} Kbps")
    rate_dict[window_size][sender_timeout][receiver_timeout] = data_rate

with open('rate_dict.json', 'w') as f:
    json.dump(rate_dict, f)
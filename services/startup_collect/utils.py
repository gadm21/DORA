

import time, datetime, os, re, argparse

from bluepy.btle import BTLEDisconnectError

from miband import miband

project_dir = '/home/pi/Desktop/HeleLora/src/services/startup_collect'
auth_key_filename = 'auth_key.txt'
mac_filename = 'mac.txt'
data_dir = '/home/pi/Desktop/HeleLora/Data/X'
data_path = None
band = None
label = 0 # label of the data. can be 1 (exercise), 2 (sleeping), or 3 (studying). 0 is not valid, only a placeholder. 
# Additional labels to be added: Not active (when RPI can connect to band but the band is not weared), Not present (when the RPI cannot establish a connection with the band)
# list of lists. Each element is a list of 6 measurements at some time t. The measurements are (ordered):
# [gyro_x_delta, gryo_y_delta, gyro_z_delta, abs_delta_sum, current_HR, HR_change_rate]
timeseries_data = [] 
timeseries_maxlen = 10_000
start_time = 0
stop_flag = False



def get_args() : 
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--label', default=get_auto_label(), type = int, help='Set the label to be associated with the data that will be collection.')
    parser.add_argument('-d', '--duration', default=400, type = int, help='Set the duration (in minutes) for the script to run and collect data.')
    args = parser.parse_args()
    return args


def get_auto_label() :
	global label # 1 (exercise), 2 (sleeping), or 3 (studying)
	time_dict = get_time () 
	if time_dict['ampm'] == 'PM' :
		if time_dict['hour'] < 5 : 
			label = 3 # studying from 1 pm to 4:59 pm
		else: 
			label = 1 # excerising from 5 pm to 11:59 pm
	else : 
		if time_dict['hour'] < 8 : 
			label = 2 # sleeping from 12 am to 7:59 am
		else : 
			label = 3 # studying from 8 am to 11:59 am 
			
	assert label != 0, 'label 0 is not defined' # label should have been changed to a valid label 
	return label
			
			

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


class regex_patterns():
    mac_regex_pattern = re.compile(r'([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})')
    authkey_regex_pattern = re.compile(r'([0-9a-fA-F]){32}')


def get_mac_address(filename):
    try:
        with open(filename, "r") as f:
            hwaddr_search = re.search(regex_patterns.mac_regex_pattern, f.read().strip())
            if hwaddr_search:
                MAC_ADDR = hwaddr_search[0]
            else:
                print ("No valid MAC address found in {}".format(filename))
                exit(1)
    except FileNotFoundError:
            print ("MAC file not found: {}".format(filename))
            exit(1)
    return MAC_ADDR


def get_auth_key(filename):
    try:
        with open(filename, "r") as f:
            key_search = re.search(regex_patterns.authkey_regex_pattern, f.read().strip())
            if key_search:
                AUTH_KEY = bytes.fromhex(key_search[0])
            else:
                print ("No valid auth key found in {}".format(filename))
                exit(1)
    except FileNotFoundError:
            print ("Auth key file not found: {}".format(filename))
            exit(1)
    return AUTH_KEY



def save_dataset(is_first = False): 
    ''' 
    saves a txt file containing the data in the following format: 
    - The first line contains the label, which can be either 1 (exercise), 2 (sleeping), or 3 (studying). 
    - Each of the following line will either contain 4 or 2 comma separated values: 
        * IF it contains 4 values, the values are for the variables ['gyro_x', 'gryo_y', 'gyro_z', 'timestamp']
        * If it contains 2 values, the values are for the variables ['heart rate', 'timestamp']
    '''
    global timeseries_data, data_path
    
    def append_line(filepath, line): 
        with open(filepath, 'a') as f :
            f.write(line)
            f.write('\n')

    if not os.path.exists(data_dir) : 
        os.makedirs(data_dir)
    
    if is_first : 
        data_path = os.path.join(data_dir, '{}.txt'.format(get_time(as_str = True)))
        append_line(data_path, get_time(as_str = True)) 
    else : 
        for datum in timeseries_data : 
            append_line(data_path, ','.join(str(d) for d in datum))
        timeseries_data = []  



   
def sensors_callback(data):
    global stop_flag, timeseries_maxlen, timeseries_data 
    tick_time = time.time() 

    data_type = data[0] 
    data = data[1] 

    if data_type == 'GYRO_RAW': 
        for datum in data : 
            current_data = [datum['gyro_raw_x'], datum['gyro_raw_y'], datum['gyro_raw_z'], tick_time]
            timeseries_data.append(current_data)
    elif data_type == 'HR' : 
        current_data = [data, tick_time]
        timeseries_data.append(current_data)
        
    if len(timeseries_data) > timeseries_maxlen :
        if timeseries_maxlen == 10_000 : # this cache size is used for the first time to force wait period before creating a data file, then this period is decreased
            save_dataset(is_first= True) # just to create the file and name it with label.
            timeseries_maxlen = 1_000
        else : 
            save_dataset()
    
    if stop_flag :
        print("stop flag:", stop_flag) 
    return stop_flag



def connect():
    global band
    success = False
    timeout = 3
    msg = 'Connection to the band failed. Trying again in {} seconds'
    
    
    MAC_ADDR = get_mac_address(os.path.join(project_dir, mac_filename))
    AUTH_KEY = get_auth_key(os.path.join(project_dir, auth_key_filename))

    while not success:
        try:
            band = miband(MAC_ADDR, AUTH_KEY, debug=True)
            success = band.initialize()
        except BTLEDisconnectError:
            print(msg.format(timeout))
            time.sleep(timeout)
        except KeyboardInterrupt:
            print("\nExit.")
            exit()


def start_data_pull(duration, label):
    global start_time
    start_time = time.time() 
    while True:
        try:
            band.start_heart_and_gyro(sensitivity=1, callback=sensors_callback, start_time = start_time, duration = duration)
            if int(time.time() - start_time) > duration * 60 : 
                save_dataset() 
                return  
             
        except BTLEDisconnectError:
            band.gyro_started_flag = False
            connect()





#!/usr/bin/env python3

# TODO : disable and enable bluetooth with python or .sh to be used when RPI needs
# to connect to LoRa at some time and need to connect to watch (bluetooth) at other times. 

import argparse 
from bluepy.btle import BTLEDisconnectError
import pathlib

from miband import miband

from utils import * 




#-------------------------------------------------------------------------#




if __name__ == "__main__":
    args = get_args()
    
    connect()
    start_data_pull(args.duration, args.label)
    print("Done")
    
    
    
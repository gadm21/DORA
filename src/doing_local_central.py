
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder


# import seaborn as sns
from keras.models import Sequential
# from tensorflow.keras.layers import Dense,Dropout, MaxPooling1D
from tensorflow.keras.utils import to_categorical
# from tensorflow.keras.callbacks import CSVLogger, EarlyStopping
import copy

import tensorflow as tf 


import torch 
import torch.nn as nn
import torch.nn.functional as F
# import transforms

import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
from torch.optim.lr_scheduler import StepLR
import torchvision.transforms as transforms

import opacus
from opacus import PrivacyEngine
from tqdm  import tqdm
import torch.utils.data as torch_data

# import tensorflow_privacy.privacy.privacy_tests.membership_inference_attack.membership_inference_attack as mia
# from tensorflow_privacy.privacy.membership_inference_attack.data_structures import AttackInputData
# from tensorflow_privacy.privacy.membership_inference_attack.data_structures import SlicingSpec
# from tensorflow_privacy.privacy.membership_inference_attack.data_structures import AttackType
# import tensorflow_privacy.privacy.membership_inference_attack.plotting as plotting


from data_utils import get_depth_data, HARDataset,get_dataset 
from model_utils import * 
from utils import * 


datasets = ['hars', 'depth', 'imu']

for dataset in datasets : 
    
    central_train_set, central_test_set, public_set, local_sets, test_sets = get_dataset(dataset)

    central_train_dataset = torch_data.TensorDataset(torch.tensor(central_train_set[0]), torch.tensor(central_train_set[1]))
    central_test_dataset = torch_data.TensorDataset(torch.tensor(central_test_set[0]), torch.tensor(central_test_set[1]))
    central_train_dataloader = DataLoader(central_train_dataset, batch_size = 32, shuffle = True)
    central_test_dataloader = DataLoader(central_test_dataset, batch_size = 32, shuffle = True)



    # Central Training
    central_train_sets = [central_train_set for i in range(len(local_sets))]
    central_test_sets = [central_test_set for i in range(len(local_sets))]



    fl_params = {
        'client_num': len(local_sets),
        'tot_T': 100, 
        'C': 1.0,
        'local_sets': central_train_sets,
        'test_sets': central_test_sets,
        'public_set': public_set,
        'batch_size': 32,
        'epochs': 2, 
        'lr': 0.01,
        'aggregate': 'soft_labels', # 'grads', 'compressed_soft_labels', 'soft_labels'
        'default_client_id': 1, # 0 small model, 1 medium model, 2 large model
        'augment': False, 
        'private': False, 
        'max_grad_norm': 1.0,
        'delta': 1e-4,
        'epsilon': 4,
        'local_benchmark_epochs': 100
    }

    exp_path = f"../results/{dataset}/{fl_params['aggregate']}_C{fl_params['C']}"
    fl_params['exp_path'] = exp_path
    server = FLServer(fl_params)

    FL_acc = []
    # for t in range(fl_params['tot_T']):
    #     acc = server.global_update()
    #     FL_acc.append(acc)
    #     print(f"Round {t} accuracy: {acc}")
    
    cient_accs = []
    i = 5
    for client in server.clients:
        acc = client.local_benchmark()
        cient_accs.append(acc)
        i -= 1
        if i == 0:
            break
    
    print(f"Average of dataset {dataset} is {np.mean(cient_accs)}")
        

    # server.save_assets()

# attack_res = run_mia_attack(server.clients[0].model, server.clients[0].local_dl, server.clients[0].test_dl) 

# f = open('mia_results.txt', 'w')
# f.write(str(attack_res.summary(by_slices = True)))
# f.close()

# # plot central training accuracy and federated learning accuracy 
# # plt.plot(central_acc, label = 'Central Training')
# plt.plot(FL_acc, label = 'Federated Learning')
# plt.legend()
# plt.show()



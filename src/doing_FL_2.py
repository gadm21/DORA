
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
from itertools import product
import torch

from data_utils import get_harbox_data, get_dataloader_from_numpy, get_dataset
from model_utils import *
from utils import FLClient, FLServer
from data.large_scale_HARBox import data_pre as harbox_pre










datasets = [ 'harbox'] 
Cs = [ 1.0]
aggregation_methods = [ 'soft_labels']
HT = [False]
Augment = [True, False]
Private = [ False]
Weighting = ['unifrom', 'performance_based']
n_pub_setss = [1, 4]

for dataset, C, aggregation_method, ht, aug, weighting, n_pub_sets, dp in product(datasets, Cs, aggregation_methods, HT, Augment, Weighting, n_pub_setss, Private):


    print(f"Starting FL experiment with {dataset} dataset, C = {C}, aggregation method = {aggregation_method}, hyperparameter tuning = {ht}, augment = {aug}, weighting = {weighting}, n_pub_sets = {n_pub_sets}, private = {dp}")
    central_train_set, central_test_set, _, local_sets, test_sets = get_dataset(dataset, n_pub_sets = n_pub_sets) 
    _, _, public_set, _, _ = get_dataset('imu', n_pub_sets = n_pub_sets) 
    
    print('local sets: ', len(local_sets))
    fl_params = {
        'client_num': len(local_sets),
        'tot_T': 50, 
        'C': C,
        'local_sets': local_sets,
        'test_sets': test_sets,
        'public_set': public_set,
        'batch_size': 32,
        'epochs': 4, 
        'lr': 0.01,
        'aggregate': aggregation_method, # 'grads', 'compressed_soft_labels', 'soft_labels'
        'hyperparameter_tuning': ht, 
        'weighting': weighting, # 'uniform', 'performance_based'
        'default_client_id': 1, 
        'augment': aug, 
        'private': dp, 
        'max_grad_norm': 1.0,
        'delta': 1e-4,
        'epsilon': 5,
        'local_benchmark_epochs': 50
    }

    exp_path = f"../results_HARBOX_IMU/N_pub{n_pub_sets}/{dataset}/Agg{fl_params['aggregate']}_C{fl_params['C']}_HT{fl_params['hyperparameter_tuning']}_Aug{fl_params['augment']}_W{fl_params['weighting']}"
    fl_params['exp_path'] = exp_path
    server = FLServer(fl_params)

    FL_acc = []
    for t in range(fl_params['tot_T']):
        acc = server.global_update()
        FL_acc.append(acc)
        print(f"Round {t} accuracy: {acc}")
    print("Final accuracy: ", FL_acc[-1])
    print() 
    
    client_accs = []
    for client in server.clients:
        acc = client.local_benchmark()
        client_accs.append(acc)
        break 
        # print(f"Client {client.client_id} local benchmark accuracy: {acc}")
    print("Client accuracies: ", client_accs, "  ", np.mean(client_accs))
    print()
    
    server.save_assets()



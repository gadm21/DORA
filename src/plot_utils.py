
# import plotting libraries
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import numpy as np 
import os
from os.path import join

from data_utils import get_dataset 

from functools import reduce
from scipy.signal import savgol_filter 
import matplotlib.colors as mcolors
from itertools import product

csfont = {'fontname':'Arial'}



def plot_bar_method_comparison(n_parties, method1, method2, labels, colors):
    # plot accuracy gains per model, on two tasks: method1/2[0] and method1/2[1]


    fig, ax = plt.subplots(1, 2, figsize = (15, 4))

    ax[0].bar(np.arange(n_parties) - 0.2, method1[0], label = labels[0], color = colors[0], width = 0.4)
    ax[0].bar(np.arange(n_parties) + 0.2, method1[1], label = labels[1], color = colors[1], width = 0.4) 
    ax[0].set_title('Accuracy gains per model (Non-i.i.d)')
    ax[0].set_xlabel('Parties')
    ax[0].set_ylabel('Accuracy gain (%)')
    ax[0].set_xticks(np.arange(n_parties))
    ax[0].set_xticklabels(['P' + str(i) for i in range(n_parties)])
    ax[0].legend()

    ax[1].bar(np.arange(n_parties) - 0.2, method2[0], label = labels[0], color = colors[0], width = 0.4)
    ax[1].bar(np.arange(n_parties) + 0.2, method2[1], label = labels[1], color = colors[1], width = 0.4)
    ax[1].set_title('Accuracy gains per model (i.i.d)')
    ax[1].set_xlabel('Parties')
    ax[1].set_ylabel('Accuracy gain (%)')
    ax[1].set_xticks(np.arange(n_parties))
    ax[1].set_xticklabels(['P' + str(i) for i in range(n_parties)])
    ax[1].legend()





def savgol_smooth(signal, window_len = 11, polyorder = 3) : 
    return savgol_filter(signal, window_length= window_len, polyorder = polyorder)

def get_csv_files(dir) : 
    return [join(dir, f) for f in os.listdir(dir) if f.endswith('.csv')]


class Method : 

    def __init__(self, root) : 
        self.root = root 
        self.colors = list(mcolors.TABLEAU_COLORS.keys())
        n_parties = len(os.listdir(root))
        self.client_dirs = [join(root, 'client_' + str(i)) for i in range(n_parties)]
        self.stats = [self.read_stats() for client_dir in self.client_dirs]
    
    def read_stats(self, idx = 0) :
        client_dir = self.client_dirs[idx]
        df = pd.read_csv(join(client_dir, 'central_log.csv'))
        local_acc, local_loss = df['local_acc'].values, df['local_loss'].values
        df = pd.read_csv(join(client_dir, 'fl_log.csv'))
        fl_acc, fl_loss = df['fl_acc'].values, df['fl_loss'].values 
        

        return {
            'local_acc' : local_acc,
            'local_loss' : local_loss,
            'fl_acc' : fl_acc,
            'fl_loss' : fl_loss
        }

    def plot(self, signal_name, title = 'Accuracy', smooth = False, parties_limit = None, epochs_limit = None) : 
        
        n_parties = len(self.stats)
        signals = [self.stats[i][signal_name] for i in range(n_parties)]
        labels = ['client ' + str(i) for i in range(n_parties)]
        n_epochs = len(signals[0]) 
        epochs = np.arange(n_epochs) 
        n_parties = len(signals) 
        if parties_limit is None : 
            parties_limit = n_parties 
        plt.figure(figsize=(20, 11))

        plt.subplot(2, 2, 1)
        for i in range(parties_limit) : 
            signal = signals[i]
            if smooth :
                signal = savgol_smooth(signal)
            if epochs_limit is not None : 
                signal = signal[:epochs_limit]
            
            plt.plot(epochs, signal, label=labels[i], color = self.colors[i])
        plt.legend(loc='best', bbox_to_anchor=(0.95, 0.5))
        plt.title(title) 
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.xlim(0, n_epochs)
        plt.show()
        # save figure as pdf 
        plt.savefig(join('../plots', signal_name + '.pdf'), bbox_inches='tight')



def plot_fedMD_like_comparison(left, center, right, labels = None, shades = None, title = None, limit = None) :
    n_epochs = len(center[0]) 
    epochs = np.arange(n_epochs) 
    n_parties = len(center)
    if limit is None : 
        limit = n_parties 
    plt.figure(figsize=(20, 11))
    colors = list(mcolors.TABLEAU_COLORS.keys())
    plt.subplot(2, 2, 1)
    for i in range(limit) : 
        plt.hlines(y=left[i], xmin=-10, xmax=10, linestyle = '--', color = colors[i])
        plt.hlines(y=right[i], xmin=n_epochs-10, xmax=n_epochs+10, linestyle = '--', color = colors[i])
        plt.plot(epochs, center[i], label=labels[i], color = colors[i])
        if shades is not None :
            plt.fill_between(epochs, shades[i][0], shades[i][0], alpha=0.1, color = colors[i])
    plt.legend(loc='lower right', bbox_to_anchor=(0.95, 0.5))
    plt.title(title) 
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.xlim(0, n_epochs)
    plt.show()



datasets = {
    'harbox': {
        'n_parties': 115,
    },
    'depth': {
        'n_parties': 8,
    },
    'hars': {
        'n_parties': 9,
    },
    'imu': {
        'n_parties': 9,
    }
}

print(os.listdir('../thesis_results/DPTrue/N_pub1/depth/Agggrads_C1.0_HTFalse_AugFalse_Wperformance_based'))

datasets = ['depth', 'hars', 'imu', 'harbox'] 
Cs = ['1.0', '0.5']
HTs = ['True', 'False'] 
DPs = ['True', 'False'] 
Augs = ['True', 'False'] 
Ws = ['performance_based', 'uniform']
aggs = ['soft_labels', 'grads']
n_pub_setss = ['1']

df = pd.DataFrame(columns = ['Agg', 'DP', 'C', 'W', *datasets])

local_scores = {dataset : [] for dataset in datasets}
methods_to_datasets = {} 

for dataset, C, HT, DP, Aug, W, agg, n_pub_sets in product(datasets, Cs, HTs, DPs, Augs, Ws, aggs, n_pub_setss) :
    # n_parties = datasets[dataset]['n_parties']
    method1_dir = '../results_HARBOX_IMU' + '/tightDP' + DP + '/N_pub' + n_pub_sets + '/' + dataset + '/' + 'Agg' + agg + '_C' + C + '_HT' + HT + '_Aug' + Aug + '_W' + W + '/'
    if not os.path.exists(method1_dir) :
        print('no method found')
        continue
    try : 
        
        method_name = '{}|{}|{}|{}|{}|{}'.format(C, HT, DP, Aug, W, agg)
        if method_name not in methods_to_datasets :
            methods_to_datasets[method_name] = {d: 0 for d in datasets}

        m = Method(method1_dir) 
        states = m.read_stats() 
        fl_acc, local_acc = np.max(states['fl_acc']), np.max(states['local_acc'])
        fl_acc_last, local_acc_last = states['fl_acc'][-1], states['local_acc'][-1]

        local_scores[dataset].append(round(local_acc_last, 3))
        methods_to_datasets[method_name][dataset] = round(fl_acc_last, 3)




    except Exception as e :
        print('no method:', method1_dir)
        print(e)
        continue

apply_DP = 'True'
for method, scores in methods_to_datasets.items() :
    
    C, HT, DP, Aug, W, agg = method.split('|')
    if DP != apply_DP :
        continue 
    if agg == 'soft_labels': 
        if Aug == 'True' : 
            agg = 'FedAKD' 
        else :
            agg = 'FedMD' 
    else :
        agg = 'FedAvg'

    df = df.append({'Agg':agg, 'DP': DP, 'C': C, 'W': W, **scores}, ignore_index=True)

# sort by the method
df = df.sort_values(by=['Agg', 'C', 'W'])

print(df) 
# group by the method and average the scores
groubed_df = df.groupby(['Agg']).mean().reset_index()

print('-----------------------')
for d in datasets : 
    print('dataset:', d, ' ', np.mean(local_scores[d]))
print('-----------------------')
# Sort by the method
df.to_csv('../results_HARBOX_IMU/all_results{}.csv'.format(apply_DP), index = False)
groubed_df.to_csv('../results_HARBOX_IMU/all_results_{}_grouped.csv'.format(apply_DP), index = False)
print(df.head()) 
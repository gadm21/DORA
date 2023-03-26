# Libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import pi
import os 
from utils import Experiment
 
# Set data
# df = pd.DataFrame({
# 'group': ['A','B','C','D'],
# 'var1': [38, 1.5, 30, 4],
# 'var2': [29, 10, 9, 34],
# 'var3': [8, 39, 23, 24],
# 'var4': [7, 31, 33, 14],
# 'var5': [28, 15, 32, 14]
# })

# print(df) 
dataset = 'harbox' 
aggregate = 'soft_labels'
C = 1.0
ht = True 
dp = False
aug = True 
ws = ['uniform', 'performance_based']
uniform_fl_path = f'../results/{dataset}/Agg{aggregate}_C{C}_HT{ht}_DP{dp}_Aug{False}_W{ws[0]}'
performance_based_fl_path = f'../results/{dataset}/Agg{aggregate}_C{C}_HT{ht}_DP{dp}_Aug{True}_W{ws[1]}'
exp1_params = {'exp_path': uniform_fl_path, 'name': 'FedMD' , 'aggregate': aggregate, 'C': C}
exp2_params = { 'exp_path': performance_based_fl_path , 'name': 'FedAKD', 'aggregate': aggregate, 'C': C}

uniform_fl = Experiment(exp1_params).get_fl_acc(avg = False) 
performance_based_fl = Experiment(exp2_params).get_fl_acc(avg = False)


df_dict = {
    'group': [exp1_params['name'], exp2_params['name']]} 
for i in range(len(uniform_fl)):
    df_dict['Client ' + str(i)] = [uniform_fl[i], performance_based_fl[i]]

df = pd.DataFrame(df_dict)


print(df) 

 
# ------- PART 1: Create background
 
# number of variable
categories=list(df)[1:]
N = len(categories)
 
# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]
 
# Initialise the spider plot
ax = plt.subplot(111, polar=True)
 
# If you want the first axis to be on top:
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
 
# Draw one axe per variable + add labels
print("categories: ", categories)
plt.xticks(angles[:-1][::5], categories[::5])
 
# Draw ylabels
ax.set_rlabel_position(0)
plt.yticks([0.3, 0.5, 0.7], ["0.3","0.5","0.7"], color="grey", size=7)
plt.ylim(0,1)
 

# ------- PART 2: Add plots
 
# Plot each individual = each line of the data
# I don't make a loop, because plotting more than 3 groups makes the chart unreadable
 
# Ind1
values=df.loc[0].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label=df.group[0])
ax.fill(angles, values, 'b', alpha=0.1)
 
# Ind2
values=df.loc[1].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label=df.group[1])
ax.fill(angles, values, 'r', alpha=0.1)
 
# Add legend
plt.legend(loc = 'lower right', bbox_to_anchor=(0.1, 0.1)) 

# Show the graph
plt.show()

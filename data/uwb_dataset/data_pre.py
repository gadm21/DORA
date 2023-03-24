from PIL import Image
import cv2 as cv
import numpy as np
np.set_printoptions(threshold = np.inf)
import matplotlib.pyplot as plt
from skimage import data_dir,io,color
from sklearn.model_selection import train_test_split
import random
random.seed(0)

cluster_set = ['parking_','corridor_', 'room_']#3,3,3
class_set = ['_static','_walk']
label = [1,-1]#[0,1]

NUM_OF_CLASS = 2
NUM_OF_CLUSTER = 3
DIMENSION_OF_FEATURE = 55


def load_data(user_id):

	# dataset append and split
	x_coll = []
	y_coll = []

	if user_id < 2:
		cluster_id = 0
		intra_user_id = user_id + 2 # 0，1 to 2,3
	elif user_id < 5:
		cluster_id = 1
		intra_user_id = user_id - 1 # 2,3,4 to 1,2,3
	else:
		cluster_id = 2
		intra_user_id = user_id - 4 # 5,6,7 to 1,2,3

	# x append
	cluster_des = str(cluster_set[cluster_id])

	for class_id in range(NUM_OF_CLASS):
	
		read_path = './' + \
		cluster_des + str(intra_user_id) + str(class_set[class_id]) + '_add.txt'

		temp_original_data = np.loadtxt(read_path,delimiter=',')
		temp_coll = temp_original_data#temp_original_data.reshape(-1, DIMENSION_OF_FEATURE)
		count_img = temp_coll.shape[0]
		temp_label = label[class_id] * np.ones(count_img)

		# print(temp_original_data.shape)
		# print(temp_coll.shape)

		x_coll.extend(temp_coll)
		y_coll.extend(temp_label)

	x_coll = np.array(x_coll)
	y_coll = np.array(y_coll)

	print(x_coll.shape)
	print(y_coll.shape)

	return x_coll, y_coll, DIMENSION_OF_FEATURE


def generate_data(num_of_train_per_node, num_of_test_per_node, x_coll, y_coll):

	node_x_train = np.zeros((num_of_train_per_node, DIMENSION_OF_FEATURE))
	node_y_train = np.zeros(num_of_train_per_node)
	node_x_test = np.zeros((num_of_test_per_node, DIMENSION_OF_FEATURE))
	node_y_test = np.zeros(num_of_test_per_node)

	test_percent = 0.55

	# samples in each node
	num_of_all_train_data = int(x_coll.shape[0] * (1 - test_percent))
	num_of_all_test_data = x_coll.shape[0] - num_of_all_train_data

	x_train,x_test,y_train,y_test = \
	train_test_split(x_coll,y_coll,test_size = test_percent,random_state = 0)

	# print(num_of_all_train_data)
	# print(num_of_all_test_data)
	# print(x_train.shape[0])

	train_index = random.sample(range(0,num_of_all_train_data), num_of_train_per_node)
	test_index = random.sample(range(0,num_of_all_test_data), num_of_test_per_node)

	# print(train_index)
	# print(test_index)

	# train sample in one node
	for train_id in range(num_of_train_per_node):

		node_x_train[train_id, :] = np.array(x_train[train_index[train_id]]).flatten().astype('float32')
		node_y_train[train_id] = y_train[train_index[train_id]].astype('float32')
	node_y_train = node_y_train.reshape(-1,1)

	# test sample of one class in one node
	for test_id in range(num_of_test_per_node):
		node_x_test[test_id, :] = np.array(x_test[test_index[test_id]]).flatten().astype('float32')
		node_y_test[test_id] = y_test[test_index[test_id]].astype('float32')
	node_y_test = node_y_test.reshape(-1,1)
	
	return node_x_train, node_y_train, node_x_test, node_y_test


def count_analysis(y):

	count_class = np.zeros(NUM_OF_CLASS)

	for class_id in range(NUM_OF_CLASS):
		count_class[class_id] = np.sum( y == label[class_id])

	return count_class

# NUM_OF_USERS = 10
# NUM_TRAIN_EXAMPLES_PER_USER = (40 * np.ones(NUM_OF_USERS)).astype(int)
# NUM_TEST_EXAMPLES_PER_USER = (20 * np.ones(NUM_OF_USERS)).astype(int)

# [x_coll, y_coll, D] = load_data()

# node_train_index= node_define(NUM_TRAIN_EXAMPLES_PER_USER, NUM_OF_USERS)
# node_test_index= node_define(NUM_TEST_EXAMPLES_PER_USER, NUM_OF_USERS)

# (x_train, y_train, x_test, y_test) = \
# generate_data(NUM_TRAIN_EXAMPLES_PER_USER, NUM_TEST_EXAMPLES_PER_USER, NUM_OF_USERS, node_train_index, node_test_index, x_coll, y_coll)

# count_train_class = count_analysis(y_train, node_train_index, NUM_OF_USERS)
# count_test_class = count_analysis(y_test, node_test_index, NUM_OF_USERS)
# print(count_train_class)
# print(count_test_class)


# print(x_train.shape)
# print(x_test.shape)
# print(y_train.shape)
# print(y_test.shape)
# print(y_test)

NUM_OF_TOTAL_USERS = 8
count_user_data = np.zeros(NUM_OF_TOTAL_USERS)


#load data 
for current_user_id in range(NUM_OF_TOTAL_USERS):
	print("USER:", current_user_id)
	x_coll, y_coll, dimension = load_data(current_user_id)
	print(count_analysis(y_coll))
	count_user_data[current_user_id] = y_coll.shape[0]

print(np.min(count_user_data))
print(np.max(count_user_data))
print(np.mean(count_user_data))
print(np.std(count_user_data))





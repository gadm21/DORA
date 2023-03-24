from PIL import Image
import cv2 as cv
import numpy as np
import os 

np.set_printoptions(threshold = np.inf)
import matplotlib.pyplot as plt
from skimage import data_dir,io,color
from sklearn.model_selection import train_test_split
import random
random.seed(0)

environment = ['outdoor/', 'indoor_normal/', 'indoor_dark/']
gesture = ['/good','/ok','/victory','/stop','/fist']
label = [0,1,2,3,4]

NUM_OF_CLASS = 5
NUM_OF_CLUSTER = 3     #each node will only have one cluster
# DIMENSION_OF_IMG = 36
DIMENSION_OF_IMG = 30
DIMENSION_OF_FEATURE = int(DIMENSION_OF_IMG*DIMENSION_OF_IMG)
NUM_OF_TOTAL_USERS = 9


def load_depth_data_train(user_id):

	# dataset append and split
	x_coll = []
	y_coll = []

	cluster_id = int(user_id / NUM_OF_CLUSTER)
	cluster_des = str(environment[cluster_id])

	for class_id in range(NUM_OF_CLASS):
	
		read_path =  cluster_des + 'Node'+ str(user_id) + str(gesture[class_id]) +'/*.png'
		read_path = os.path.join(os.path.dirname(__file__), read_path)
		# print(read_path)
		temp_original_img = io.ImageCollection(read_path)
		count_img = len(temp_original_img)
		resize_temp_coll = []

		for im in range(count_img):
			temp_array = temp_original_img[im]
			arr2im = (Image.fromarray(temp_array)).convert('L')
			arr2im = arr2im.resize((DIMENSION_OF_IMG, DIMENSION_OF_IMG))
			temp_array = np.array(arr2im)
			resize_temp_coll.append(temp_array)

		temp_coll = np.array(resize_temp_coll)
		temp_label = class_id * np.ones(count_img)

		# print(temp_original_data.shape)
		#print(temp_coll.shape)

		x_coll.extend(temp_coll)
		y_coll.extend(temp_label)

	x_coll = np.array(x_coll)
	y_coll = np.array(y_coll)
	
	# print("xcoll::", x_coll.shape)
	# print(y_coll.shape)

	return x_coll, y_coll

def load_depth_data_test(user_id):

	# dataset append and split
	x_coll = []
	y_coll = []

	cluster_id = int(user_id / NUM_OF_CLUSTER)
	cluster_des = str(environment[cluster_id])

	for class_id in range(NUM_OF_CLASS):
	
		read_path = cluster_des + 'test' + str(gesture[class_id])+ '/*.png'
		read_path = os.path.join(os.path.dirname(__file__), read_path)
		#print(read_path)
		temp_original_img = io.ImageCollection(read_path)
		count_img = len(temp_original_img)
		resize_temp_coll = []

		for im in range(count_img):
			temp_array = temp_original_img[im]
			arr2im = (Image.fromarray(temp_array)).convert('L')
			arr2im = arr2im.resize((DIMENSION_OF_IMG, DIMENSION_OF_IMG))
			temp_array = np.array(arr2im)
			resize_temp_coll.append(temp_array)

		temp_coll = np.array(resize_temp_coll)
		temp_label = class_id * np.ones(count_img)

		# print(temp_original_data.shape)
		#print(temp_coll.shape)

		x_coll.extend(temp_coll)
		y_coll.extend(temp_label)

	x_coll = np.array(x_coll)
	y_coll = np.array(y_coll)
	
	# print(x_coll.shape)
	# print(y_coll.shape)

	return x_coll, y_coll

def generate_depth_gesture(num_of_train_per_node, x_coll, y_coll):
	
	x_train = x_coll
	y_train = y_coll
	node_x_train = np.zeros((num_of_train_per_node, DIMENSION_OF_FEATURE))
	node_y_train = np.zeros(num_of_train_per_node)
	train_index = np.zeros(num_of_train_per_node)

	num_of_all_train_data = int(x_coll.shape[0])
	train_index = random.sample(range(0,num_of_all_train_data), num_of_train_per_node)

    # train sample in one node
	for train_id in range(num_of_train_per_node):
		node_x_train[train_id, :] = np.array(x_train[train_index[train_id]]).flatten().astype('float32') / 255.0
		node_y_train[train_id] = y_train[train_index[train_id]]

 
	return node_x_train, node_y_train



def count_analysis(y, index, num_of_user):

	count_class = np.zeros((num_of_user,NUM_OF_CLASS))

	for user_id in range(num_of_user):
		for class_id in range(NUM_OF_CLASS):
			count_class[user_id,class_id] = np.sum( y[index[user_id]] == class_id)

	return count_class



if __name__ == "__main__" : 
	
	count_user_data = np.zeros(NUM_OF_TOTAL_USERS)


	#load data 
	for current_user_id in range(NUM_OF_TOTAL_USERS):
		print("USER:", current_user_id)
		x_coll, y_coll, dimension = load_depth_data_train(current_user_id)
		print(count_analysis(y_coll))
		count_user_data[current_user_id] = y_coll.shape[0]

	print(np.min(count_user_data))
	print(np.max(count_user_data))
	print(np.mean(count_user_data))
	print(np.std(count_user_data))






import glob
import os
import subprocess
import tensorflow as tf
import sys
import json
import numpy as np
import time
import re

#shut up warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"]="2"

"""
Function that checks whether images are scored and if not scores them based on our deep learning models. 

Input: folder that includes images
output: rating in json format in results directory.

example: python main.py collegas

dependencies: models folder which includes models that can be used for scoring and some test images in a supplied folder (e.g. "collegas")
"""

# Directory where all models and model labels are stored

output_dir = "results"
# images_path = sys.argv[1]

# Main model that scores an image based on a path
def main_model(image_path):
	cwd = os.getcwd()
	model_dir= os.path.join(cwd, 'models/Complete_Model/models')
	
	# Read in the image_data
	print('modeldir:', model_dir)
	image_data = tf.gfile.FastGFile(image_path, 'rb').read()

	# # Text File where results are written (backup)
	# filename = "results_full.txt" 
	# with open(filename, 'a+') as f:
	# 	# Write a first line defining the image filename
	# 	f.write('\n%s\n' % (image_path))

	# Setup the JSON file that will be used and create some features used for identification.
	char_name = image_path.split('/')[-1]
	# char_name = re.findall('(?<=/)\w+', image_path)[0]
	output_data = {"name": char_name,
				"timestamp": time.time(),
				"url": image_path}  

	# Features will be a list that will be appended based on model outputs
	output_data["features"] = []  

	# Read model names from provided directory
	model_names = glob.glob(model_dir+"/*")
	model_names = [x.replace(model_dir+"/",'') for x in model_names]
	print("Model names found are: ", model_names)

	# Create results directory if it does not already exists
	if not os.path.exists(output_dir):
		os.system("mkdir {}".format(output_dir))

	# Loop over models
	for model in model_names:
		# Loads label file
		label_location = model_dir + "/" + model + "/labels.txt"
		label_lines = [line.rstrip() for line 
						   in tf.gfile.GFile(label_location)]

		# Within this context set a default graph
		with tf.Graph().as_default():
			# Load graph from location
			graph_location = model_dir + "/" + model + "/retrained_graph.pb"
			with tf.gfile.FastGFile(graph_location, 'rb') as f:
				graph_def = tf.GraphDef()
				graph_def.ParseFromString(f.read())
				_ = tf.import_graph_def(graph_def, name='')

				with tf.Session() as sess:
					# Feed the image_data as input to the graph and get first prediction
					softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
					
					predictions = sess.run(softmax_tensor, \
							 {'DecodeJpeg/contents:0': image_data})
					
					# Sort to show labels of first prediction in order of confidence
					top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
					# top k returns index of best value
					# predictions returns predicted scores
					print("----Scoring: ", model)
					for node_id in top_k:
						# get label
						human_string = label_lines[node_id]
						# get score
						score = predictions[0][node_id]
						print('%s (score = %.5f)' % (human_string, score))
					print("\n")

					# # Write results from this model to text file
					# filename = "results_full.txt"    
					# with open(filename, 'a+') as f:
					#     for node_id in top_k:
					#         human_string = label_lines[node_id]
					#         score = predictions[0][node_id]
					#         f.write('%s %.2f\n' % (human_string, score))

					# Json needs int instead of float so move to percentage
					score = int(np.round(predictions[0][top_k[0]]*100))
					output_data["features"].append({
						"key": model,
						"value": label_lines[top_k[0]],
						"score": score})
	return output_data


	# # Write JSON file which stores results
	# file_name = image_path.replace(images_path, "")
	# with open(output_dir+"/"+file_name+'.txt', 'w') as outfile:  
	# 	json.dump(output_data, outfile)


# if __name__ == "__main__":
# 	# Find all images in the folder provided

# 	# images =  glob.glob(images_path+"/*")
# 	# images = [x.replace(images_path+"/",'') for x in images]

# 	# # Look if these are scored and if not score them
# 	# for item in images:
# 	# 	if not os.path.exists(output_dir+"/"+item+".txt"):
# 	# 		print("Scoring new image: {}".format(item))
# 	# 		im_location = images_path+"/"+item
# 	# 		main(im_location)
# 	# print('Done Scoring Images')

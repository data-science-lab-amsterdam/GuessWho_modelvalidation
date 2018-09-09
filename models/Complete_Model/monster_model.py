# Script to create labels
import tensorflow as tf
import sys
import json
import numpy as np
import glob
import os

#shut up warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"]="2"

# will take first argument as path for the image
image_path = sys.argv[1]

# Read in the image_data
image_data = tf.gfile.FastGFile(image_path, 'rb').read()

# Directory where all models and model labels are stored
model_dir = "models"
output_dir = "results"

# Read model names from provided directory
model_names = glob.glob(model_dir+"/*")
model_names = [x.replace(model_dir+"/",'') for x in model_names]
print("Model names found are: ", model_names)

# Text File where results are written (backup)
filename = "results_full.txt" 
with open(filename, 'a+') as f:
	# Write a first line defining the image filename
	f.write('\n%s\n' % (image_path))

# Setup the JSON file that will be used
output_data = {}  
output_data[image_path] = []  

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
					#print(node_id)
					# get label
					human_string = label_lines[node_id]
					# get score
					score = predictions[0][node_id]
					print('%s (score = %.5f)' % (human_string, score))
				print("\n")

				# Write results from this model to text file
				filename = "results_full.txt"    
				with open(filename, 'a+') as f:
				    for node_id in top_k:
				        human_string = label_lines[node_id]
				        score = predictions[0][node_id]
				        f.write('%s %.2f\n' % (human_string, score))

				# Json needs int instead of float so move to percentage
				score = int(np.round(predictions[0][top_k[0]]*100))
				output_data[image_path].append({
					model: label_lines[top_k[0]],
					"score": score})


# Write JSON file
file_name = image_path.replace("test_images", "")
with open(output_dir+"/"+file_name+'.txt', 'w') as outfile:  
	json.dump(output_data, outfile)

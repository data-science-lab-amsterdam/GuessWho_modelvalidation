import glob
import tensorflow as tf
import json
import numpy as np
import time
import re
import logging
from pathlib import Path

"""
Function that checks whether images are scored and if not scores them based on our deep learning models. 

Input: folder that includes images
output: rating in json format in results directory.

example: python main.py collegas

dependencies: models folder which includes models that can be used for scoring and some test images in a supplied folder (e.g. "collegas")
"""


def predict(image_path):
    """
    Main model that scores an image based on a path
    """
    # Read in the image_data
    image_data = tf.gfile.FastGFile(image_path, 'rb').read()

    # Setup the JSON file that will be used and create some features used for identification.
    output_data = {
        'name': Path(image_path).name,
        'timestamp': time.time(),
        'url': image_path,
        'features': []  # Features will be a list that will be appended based on model outputs
    }

    # Read model names from provided directory
    model_dirs = glob.glob(str(Path('./models') / '*'))
    model_names = [Path(m).name for m in model_dirs]
    logging.info("Model names found are: ", model_names)

    # Loop over models
    for model_name in model_names:
        # Loads label file
        label_location = str(Path('./models') / model_name / 'labels.txt')
        label_lines = [line.rstrip() for line in tf.gfile.GFile(label_location)]

        # Within this context set a default graph
        with tf.Graph().as_default():
            # Load graph from location
            graph_location = str(Path('./models') / model_name / 'retrained_graph.pb')
            with tf.gfile.FastGFile(graph_location, 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                _ = tf.import_graph_def(graph_def, name='')

                with tf.Session() as sess:
                    # Feed the image_data as input to the graph and get first prediction
                    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

                    predictions = sess.run(softmax_tensor,
                                           {'DecodeJpeg/contents:0': image_data}
                                           )

                    # Sort to show labels of first prediction in order of confidence
                    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
                    # top k returns index of best value
                    # predictions returns predicted scores
                    logging.info("Scoring: {}".format(model_name))
                    for node_id in top_k:
                        # get label
                        human_string = label_lines[node_id]
                        # get score
                        score = predictions[0][node_id]
                        logging.info('\t%s (score = %.5f)' % (human_string, score))

                    # Json needs int instead of float so move to percentage
                    score = int(np.round(predictions[0][top_k[0]] * 100))
                    output_data["features"].append({
                        "key": model_name,
                        "value": label_lines[top_k[0]],
                        "score": score
                    })

    # # Write JSON file which stores results
    # output_file = Path('./data/checked') / Path(image_path).name + '.txt'
    # logging.info("writing scores to {}".format(str(output_file)))
    # with open(output_file, 'w') as f:
    #     json.dump(output_data, f)
    return output_data



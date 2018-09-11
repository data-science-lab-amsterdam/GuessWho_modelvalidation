# Multi-label-Inception-net
Modified  [Inception net](https://github.com/tensorflow/models/tree/master/research/inception).

Main Code from: https://github.com/BartyzalRadek/Multi-label-Inception-net

Download fotos with Fatkun batch download: https://chrome.google.com/webstore/detail/fatkun-batch-download-ima/nnjjahlikiabnchcpehcpkdeckfgnohf

Detailed explanation of all the changes and reasons behind them: 
https://medium.com/@bartyrad/multi-label-image-classification-with-inception-net-cbb2ee538e30

# Included:
- models: models for all features to be extracted
- monster_model.py: function to extract features based on an image
- main.py: function that checks a folder for new images and scores new items. 
- results: folder where results are stored
- test_images: a few test images
- results_full: is a log to be used as a backup

## SEMI WORKING:
- Gender
- Glasses 
- Hats / Caps
- Hair lenght
- Hair colour
- Assecoires (necklace?)
- Hair Type

### Works on:
[TensorFlow 1.8.0](https://github.com/tensorflow/tensorflow/releases/tag/v1.8.0) 
[Python 3]

### Usage
Monster_model.py to be called on the command line like "python monster_model.py test_images/1.jpg" to score an individual image.
main.py to be called like "python main.py test_images"
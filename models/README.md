# Multi-label-Inception-net
Modified  [Inception net](https://github.com/tensorflow/models/tree/master/research/inception).

Main Code from: https://github.com/BartyzalRadek/Multi-label-Inception-net

Download fotos with Fatkun batch download: https://chrome.google.com/webstore/detail/fatkun-batch-download-ima/nnjjahlikiabnchcpehcpkdeckfgnohf

Detailed explanation of all the changes and reasons behind them: 
https://medium.com/@bartyrad/multi-label-image-classification-with-inception-net-cbb2ee538e30

## SEMI WORKING:
- Gender
- Glasses 
- Hats / Caps

## In progress:
- Facial Hair

## TODO:
- Hair lenght
- Hair colour
- Assecoires (necklace?)
- ?

### Works on:
[TensorFlow 1.8.0](https://github.com/tensorflow/tensorflow/releases/tag/v1.8.0) 
[Python 3]

### Usage
Models on this GIT are already trained and can be used by the label_image.py function 
example of command line code to test; "python label_image.py test_images/test1.jpg"

Output is a score based on what the model is predicting (i.e. gender/ glasses etc.)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import tensorflow as tf 

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
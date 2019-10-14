from __future__ import absolute_import, division, print_function

import argparse
import os
import numpy as np
from time import time

import tensorflow as tf
import byteps.tensorflow as bps
from tensorflow.keras import applications

bps.init()
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.visible_device_list = str(bps.local_rank())

model = tf.keras.applications.ResNet50(weights=None)

opt = tf.train.GradientDescentOptimizer(0.01)

compression = bps.Compression.fp16

opt = bps.DistributedOptimizer(opt, compression=compression)

init = tf.global_variables_initializer()
bcast_op = bps.broadcast_global_variables(0)

data = tf.random_uniform([128, 224, 224, 3])
target = tf.random_uniform([128, 1], minval=0, maxval=999, dtype=tf.int64)

def loss_function():
    logits = model(data, training=True)
    return tf.losses.sparse_softmax_cross_entropy(target, logits)

def log(s, nl=True):
    #if bps.rank() != 0:
    #    return
    print(s, end='\n' if nl else '')



with tf.Session(config=config) as session:
	init.run()
	bcast_op.run()
	loss = loss_function()
	train_opt = opt.minimize(loss)
	log('Running warmup...')
	img_secs = []
	for i in range(25):
		start = time()
		session.run(train_opt)
		img_sec = 128 / (time()-start)
		log('Iter #%d: %.1f img/sec per %s' % (i, img_sec, 'device'))

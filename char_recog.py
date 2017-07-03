import os
import random
import tensorflow.contrib.slim as slim
import time
import logging
import numpy as np
import tensorflow as tf
import pickle
import sys
from PIL import Image
from tensorflow.python.ops import control_flow_ops
import char_split

logger = logging.getLogger('char recognition')
logger.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

tf.app.flags.DEFINE_boolean('random_flip_up_down', False, "Whether to random flip up down")
tf.app.flags.DEFINE_boolean('random_brightness', True, "whether to adjust brightness")
tf.app.flags.DEFINE_boolean('random_contrast', True, "whether to random constrast")

tf.app.flags.DEFINE_integer('charset_size', 3590, "Choose the first `charset_size` characters only.")
tf.app.flags.DEFINE_integer('image_size', 32, "Needs to provide same value as in training.")
tf.app.flags.DEFINE_boolean('gray', True, "whether to change the rbg to gray")
tf.app.flags.DEFINE_integer('max_steps', 16002, 'the max training steps ')
tf.app.flags.DEFINE_integer('eval_steps', 100, "the step num to eval")
tf.app.flags.DEFINE_integer('save_steps', 1000, "the steps to save")

tf.app.flags.DEFINE_string('checkpoint_dir', '/data/checkpoint/', 'the checkpoint dir')
tf.app.flags.DEFINE_string('train_data_dir', '/data/train_test_data/train/', 'the train dataset dir')
tf.app.flags.DEFINE_string('test_data_dir', '/data/train_test_data/test/', 'the test dataset dir')
tf.app.flags.DEFINE_string('log_dir', '/data/tflog', 'the logging dir')

tf.app.flags.DEFINE_boolean('restore', False, 'whether to restore from checkpoint')
tf.app.flags.DEFINE_boolean('epoch', 1, 'Number of epoches')
tf.app.flags.DEFINE_boolean('batch_size', 128, 'Validation batch size')
tf.app.flags.DEFINE_string('mode', 'validation', 'Running mode. One of {"train", "valid", "test"}')

# gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
FLAGS = tf.app.flags.FLAGS


def build_graph(top_k):
    keep_prob = tf.placeholder(dtype=tf.float32, shape=[], name='keep_prob')
    images = tf.placeholder(dtype=tf.float32, shape=[None, FLAGS.image_size, FLAGS.image_size, 1], name='image_batch')
    labels = tf.placeholder(dtype=tf.int64, shape=[None], name='label_batch')
    is_training = tf.placeholder(dtype=tf.bool, shape=[], name='train_flag')
    with tf.device("/gpu:0"):
        with slim.arg_scope([slim.conv2d, slim.fully_connected],
                            normalizer_fn=slim.batch_norm,
                            normalizer_params={'is_training': is_training}):
            conv3_1 = slim.conv2d(images, 64, [3, 3], 1, padding='SAME', scope='conv3_1')
            max_pool_1 = slim.max_pool2d(conv3_1, [2, 2], [2, 2], padding='SAME', scope='pool1')
            conv3_2 = slim.conv2d(max_pool_1, 128, [3, 3], padding='SAME', scope='conv3_2')
            max_pool_2 = slim.max_pool2d(conv3_2, [2, 2], [2, 2], padding='SAME', scope='pool2')
            conv3_3 = slim.conv2d(max_pool_2, 256, [3, 3], padding='SAME', scope='conv3_3')
            max_pool_3 = slim.max_pool2d(conv3_3, [2, 2], [2, 2], padding='SAME', scope='pool3')
            conv3_4 = slim.conv2d(max_pool_3, 512, [3, 3], padding='SAME', scope='conv3_4')
            conv3_5 = slim.conv2d(conv3_4, 512, [3, 3], padding='SAME', scope='conv3_5')
            max_pool_4 = slim.max_pool2d(conv3_5, [2, 2], [2, 2], padding='SAME', scope='pool4')

            flatten = slim.flatten(max_pool_4)
            fc1 = slim.fully_connected(slim.dropout(flatten, keep_prob), 1024,
                                       activation_fn=tf.nn.relu, scope='fc1')
            logits = slim.fully_connected(slim.dropout(fc1, keep_prob), FLAGS.charset_size, activation_fn=None,
                                          scope='fc2')
        loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels))
        accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(logits, 1), labels), tf.float32))

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        if update_ops:
            updates = tf.group(*update_ops)
            loss = control_flow_ops.with_dependencies([updates], loss)

        global_step = tf.get_variable("step", [], initializer=tf.constant_initializer(0.0), trainable=False)
        optimizer = tf.train.AdamOptimizer(learning_rate=0.1)
        train_op = slim.learning.create_train_op(loss, optimizer, global_step=global_step)
        probabilities = tf.nn.softmax(logits)

        tf.summary.scalar('loss', loss)
        tf.summary.scalar('accuracy', accuracy)
        merged_summary_op = tf.summary.merge_all()
        predicted_val_top_k, predicted_index_top_k = tf.nn.top_k(probabilities, k=top_k)
        accuracy_in_top_k = tf.reduce_mean(tf.cast(tf.nn.in_top_k(probabilities, labels, top_k), tf.float32))

    return {'images': images,
            'labels': labels,
            'keep_prob': keep_prob,
            'top_k': top_k,
            'global_step': global_step,
            'train_op': train_op,
            'loss': loss,
            'is_training': is_training,
            'accuracy': accuracy,
            'accuracy_top_k': accuracy_in_top_k,
            'merged_summary_op': merged_summary_op,
            'predicted_distribution': probabilities,
            'predicted_index_top_k': predicted_index_top_k,
            'predicted_val_top_k': predicted_val_top_k}


def labelToAscii(l):
    f = open("/data/train_test_data/charToLabel.txt","r+")
    chardict={}
    for line in f.readlines():
        label,asc = line.strip().split(' ')[0:2]
        chardict[int(label)] = asc
    return chardict[l]


def initTF():
    sess = tf.Session()
    logger.info('========start inference============')
    # images = tf.placeholder(dtype=tf.float32, shape=[None, FLAGS.image_size, FLAGS.image_size, 1])
    # Pass a shadow label 0. This label will not affect the computation graph.
    graph = build_graph(top_k=1)
    saver = tf.train.Saver()
    ckpt = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
    if ckpt:
        saver.restore(sess, ckpt)

    return sess,graph


def recog(cropImage, sess, graph):
    #print('char_recog')
    #temp_image = Image.open(image).convert('L')
    temp_image = cropImage.resize((FLAGS.image_size, FLAGS.image_size), Image.ANTIALIAS)
    temp_image = np.asarray(temp_image) / 255.0
    temp_image = temp_image.reshape([-1, FLAGS.image_size, FLAGS.image_size, 1])


    t1 = time.time()
    predict_val, predict_index = sess.run([graph['predicted_val_top_k'], graph['predicted_index_top_k']],
                                          feed_dict={graph['images']: temp_image,
                                                     graph['keep_prob']: 1.0,
                                                     graph['is_training']: False})
    charuni=unichr(int(labelToAscii(predict_index[0][0])))

    #print "predict_val:",predict_val[0][0],"predict_index:",predict_index[0][0],"char:", charuni
    #print "used time:", time.time()-t1
    return predict_val, predict_index, charuni


if __name__=='__main__':
    t1 = time.time()
    sess, graph = initTF()
    t2 = time.time()
    print "Init TF time used:", t2 - t1

    # charuni = unichr(24320)
    # print "char:", charuni
    imageName=sys.argv[1]
    temp_image = Image.open(imageName).convert('L')

    bbox = char_split.charSplit(imageName)
    t3 = time.time()
    print "char split time used:", t3 - t2


    # val, ind, char = recog(temp_image, sess, graph)
    # print "single char test:", "val:", val[0], "char:", char.encode("utf-8")
    #
    # bbox = getcharbox.getCharBox(handle, imageName)
    # t4 = time.time()
    f = open("./text_output.txt","w")
    lines = []
    for box_index, box in enumerate(bbox):
        #box=bbox[2]

        cropImage = temp_image.crop(box)
        #cropImage = cropImage.resize((FLAGS.image_size/cropImage.size[1]*cropImage.size[0], FLAGS.image_size), Image.ANTIALIAS)
        #backg = Image.new('L',(FLAGS.image_size,FLAGS.image_size),cropImage.getpixel((0,0)))
        #backg.paste(cropImage,(FLAGS.image_size/2-cropImage.size[0]/2,5))
        #backg = Image.open("/usr/workspace/LiuYongChao/pyocr/tests/charboxtest/testcrop2.jpg").convert('L')

        print "box:", box_index
        tp = time.time()
        val, ind, char = recog(cropImage, sess, graph)
        lines.append("predict_val:"+str(val)+"predict_index:"+str(ind)+"char:"+char.encode("utf-8")+"\n")
        #lines.append(char.encode("utf-8")+" ")
        #cropImage.save('/usr/workspace/LiuYongChao/pyocr/tests/cropImage/'+str(box[0])+"-"+str(box[1])+".jpg")
        print "val:", val[0], "char:", char.encode("utf-8")
        print "recog char time used:", time.time() - tp
    f.writelines(lines)
    print "recog total time used:", time.time()-t3



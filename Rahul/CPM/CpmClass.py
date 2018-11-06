# For single hand and no body part in the picture
# ======================================================
#Rahul Notes: KALMAN_ON : not necessarily required
# ======================================================

import tensorflow as tf
from models.nets import cpm_hand_slim
import numpy as np
from utils import cpm_utils
import cv2
import time
import math
import sys,os,glob,json

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('DEMO_TYPE',
                           default_value='test_imgs/27_r.jpg',
                           # default_value='SINGLE',
                           docstring='MULTI: show multiple stage,'
                                     'SINGLE: only last stage,'
                                     'HM: show last stage heatmap,'
                                     'paths to .jpg or .png image')
tf.app.flags.DEFINE_string('model_path',
                           default_value='models/weights/cpm_hand.pkl',
                           docstring='Your model')
tf.app.flags.DEFINE_integer('input_size',
                            default_value=368,
                            docstring='Input image size')
tf.app.flags.DEFINE_integer('hmap_size',
                            default_value=46,
                            docstring='Output heatmap size')
tf.app.flags.DEFINE_integer('cmap_radius',
                            default_value=21,
                            docstring='Center map gaussian variance')
tf.app.flags.DEFINE_integer('joints',
                            default_value=21,#default = 21
                            docstring='Number of joints')
tf.app.flags.DEFINE_integer('stages',
                            default_value=6,
                            docstring='How many CPM stages')
tf.app.flags.DEFINE_integer('cam_num',
                            default_value=0,
                            docstring='Webcam device number')
tf.app.flags.DEFINE_bool('KALMAN_ON',
                         default_value=False,
                         docstring='enalbe kalman filter')
tf.app.flags.DEFINE_float('kalman_noise',
                            default_value=3e-2,
                            docstring='Kalman filter noise value')
tf.app.flags.DEFINE_string('color_channel',
                           default_value='RGB',
                           docstring='')

# Set color for each finger
joint_color_code = [[139, 53, 255],
                    [0, 56, 255],
                    [43, 140, 237],
                    [37, 168, 36],
                    [147, 147, 0],
                    [70, 17, 145]]


limbs = [[0, 1],
         [1, 2],
         [2, 3],
         [3, 4],
         [0, 5],
         [5, 6],
         [6, 7],
         [7, 8],
         [0, 9],
         [9, 10],
         [10, 11],
         [11, 12],
         [0, 13],
         [13, 14],
         [14, 15],
         [15, 16],
         [0, 17],
         [17, 18],
         [18, 19],
         [19, 20]
         ]

hands_key_points=[2,4,5,8,9,12,13,16,17,20]
hand_base_key_points= [0,4,8,12,16,20]

if sys.version_info.major == 3:
    PYTHON_VERSION = 3
else:
    PYTHON_VERSION = 2


# reading parameters from param.json

def json_to_dict(json_filepath):
    if(not os.path.isfile(json_filepath)):
        sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
    with open(json_filepath, 'r') as fp:
        var = json.load(fp)
    return var

json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(json_file_path)
num_fingers = variables['num_fingers']

class CpmClass:
    def __init__(self, base_images_dir, display_flag = False):
        ## Intialize the variables
        self.base_images_dir = base_images_dir
        self.display_flag = display_flag

        tf_device = '/gpu:0'
        with tf.device(tf_device):
            """Build graph
            """
            if FLAGS.color_channel == 'RGB':
                input_data = tf.placeholder(dtype=tf.float32, shape=[None, FLAGS.input_size, FLAGS.input_size, 3],
                                            name='input_image')
            else:
                input_data = tf.placeholder(dtype=tf.float32, shape=[None, FLAGS.input_size, FLAGS.input_size, 1],
                                            name='input_image')

            center_map = tf.placeholder(dtype=tf.float32, shape=[None, FLAGS.input_size, FLAGS.input_size, 1],
                                        name='center_map')

            self.model = cpm_hand_slim.CPM_Model(FLAGS.stages, FLAGS.joints + 1)
            self.model.build_model(input_data, center_map, 1)

        saver = tf.train.Saver()

        """Create session and restore weights
        """
        self.sess = tf.Session()

        self.sess.run(tf.global_variables_initializer())
        if FLAGS.model_path.endswith('pkl'):
            self.model.load_weights_from_file(FLAGS.model_path, self.sess, False)
        else:
            saver.restore(self.sess, FLAGS.model_path)

        self.test_center_map = cpm_utils.gaussian_img(FLAGS.input_size, FLAGS.input_size, FLAGS.input_size / 2,
                                                 FLAGS.input_size / 2,
                                                 FLAGS.cmap_radius)
        self.test_center_map = np.reshape(self.test_center_map, [1, FLAGS.input_size, FLAGS.input_size, 1])

        # Check weights
        for variable in tf.trainable_variables():
            with tf.variable_scope('', reuse=True):
                var = tf.get_variable(variable.name.split(':0')[0])
                print(variable.name, np.mean(self.sess.run(var)))

        # Create kalman filters
        if FLAGS.KALMAN_ON:
            self.kalman_filter_array = [cv2.KalmanFilter(4, 2) for _ in range(FLAGS.joints)]
            for _, joint_kalman_filter in enumerate(self.kalman_filter_array):
                joint_kalman_filter.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]],
                                                                np.float32)
                joint_kalman_filter.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
                joint_kalman_filter.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                                                               np.float32) * FLAGS.kalman_noise
        else:
            self.kalman_filter_array = None

    def get_hand_skel(self, test_img = FLAGS.DEMO_TYPE, argv = None):
        start = time.time()
        if(isinstance(test_img, bytes)):
            test_img = test_img.decode('utf-8')
        # return hand skeleton
        if(isinstance(test_img, str)):
            # test_image : filename.jpg
            test_img = cpm_utils.read_image(os.path.join(self.base_images_dir, test_img), [], FLAGS.input_size, 'IMAGE')
        elif(isinstance(test_img, np.ndarray)):
            pass # we are good

        test_img_resize = cv2.resize(test_img, (FLAGS.input_size, FLAGS.input_size))

        test_img_input = test_img_resize / 256.0 - 0.5
        test_img_input = np.expand_dims(test_img_input, axis=0)

        # Inference

        stage_heatmap_np = self.sess.run(self.model.stage_heatmap,feed_dict={'input_image:0': test_img_input,
                                                                'center_map:0': self.test_center_map})
        last_heatmap = stage_heatmap_np[len(stage_heatmap_np) - 1][0, :, :, 0:FLAGS.joints].reshape(
                (FLAGS.hmap_size, FLAGS.hmap_size, FLAGS.joints))
        last_heatmap = cv2.resize(last_heatmap, (test_img.shape[1], test_img.shape[0]))

        joint_coord_set_list=[]
        joint_coord_set = np.zeros((FLAGS.joints, 2))

        for joint_num in range(FLAGS.joints):
            joint_coord = np.unravel_index(np.argmax(last_heatmap[:, :, joint_num]),
                                           (test_img.shape[0], test_img.shape[1]))
            joint_coord_set[joint_num, :] = [joint_coord[0], joint_coord[1]]
            joint_coord_set_list.append([joint_coord[0], joint_coord[1]])
        # print(np.array(joint_coord_set).shape)
        # print(joint_coord_set)
    
        # Show visualized image
        if(self.display_flag):
            demo_img = self.visualize_result(test_img, FLAGS, stage_heatmap_np, self.kalman_filter_array)
            cv2.imshow('demo_img', demo_img.astype(np.uint8))
            if cv2.waitKey(1) == ord('q'): cv2.destroyAllWindows()

        print('fps: %.2f' % (1 / (time.time() - start)))
        print('Run took %.02f secs'%(time.time()-start))

        return joint_coord_set_list

    def get_fing_lengths(self, joint_coord_set_list, normalize = False, normalization_const = 300):
        key_points=[joint_coord_set_list[i] for i in range(len(joint_coord_set_list))]
        key_points = np.array(key_points).flatten().tolist()
        fingers_len=[]
        for x in hand_base_key_points[1:]:
            finger_len=np.sqrt((key_points[2*x]-key_points[0])**2+(key_points[2*x+1]-key_points[1])**2)
            fingers_len.append(finger_len)
        # for i in range(0,len(key_points),4):
        #     finger_len=np.sqrt((key_points[i+2]-key_points[i])**2+(key_points[i+3]-key_points[i+1])**2)
        #     fingers_len.append(finger_len)
        if(normalize):
            return np.round(np.array(fingers_len[:num_fingers])/normalization_const,4)
        else:
            return np.round(fingers_len[:num_fingers],4)

    def run(self, argv = None):
        start = time.time()
        idx = 0
        while(idx < 20):
            idx += 1
            self.get_hand_skel()
        print('BIG Run took %.02f secs'%(time.time()-start))

    def visualize_result(self, test_img, FLAGS, stage_heatmap_np, kalman_filter_array):
        t1 = time.time()

        last_heatmap = stage_heatmap_np[len(stage_heatmap_np) - 1][0, :, :, 0:FLAGS.joints].reshape(
            (FLAGS.hmap_size, FLAGS.hmap_size, FLAGS.joints))
        last_heatmap = cv2.resize(last_heatmap, (test_img.shape[1], test_img.shape[0]))
        print('hm resize time %f' % (time.time() - t1))

        t1 = time.time()
        joint_coord_set = np.zeros((FLAGS.joints, 2))

        # Plot joint colors
        if kalman_filter_array is not None:
            print(kalman_filter_array)
            for joint_num in range(FLAGS.joints):
                joint_coord = np.unravel_index(np.argmax(last_heatmap[:, :, joint_num]),
                                               (test_img.shape[0], test_img.shape[1]))
                joint_coord = np.array(joint_coord).reshape((2, 1)).astype(np.float32)
                kalman_filter_array[joint_num].correct(joint_coord)
                kalman_pred = kalman_filter_array[joint_num].predict()
                joint_coord_set[joint_num, :] = np.array([kalman_pred[0], kalman_pred[1]]).reshape((2))

                color_code_num = (joint_num // 4)
                if joint_num in [0, 4, 8, 12, 16]:
                    if PYTHON_VERSION == 3:
                        joint_color = list(map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num]))
                    else:
                        joint_color = map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num])

                    cv2.circle(test_img, center=(joint_coord[1], joint_coord[0]), radius=3, color=joint_color, thickness=-1)
                else:
                    if PYTHON_VERSION == 3:
                        joint_color = list(map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num]))
                    else:
                        joint_color = map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num])

                    cv2.circle(test_img, center=(joint_coord[1], joint_coord[0]), radius=3, color=joint_color, thickness=-1)
        else:
            print('KALMAN not ON')
            for joint_num in range(FLAGS.joints):
                joint_coord = np.unravel_index(np.argmax(last_heatmap[:, :, joint_num]),
                                               (test_img.shape[0], test_img.shape[1]))
                joint_coord_set[joint_num, :] = [joint_coord[0], joint_coord[1]]

                color_code_num = (joint_num // 4)
                if joint_num in [0, 4, 8, 12, 16]:
                    if PYTHON_VERSION == 3:
                        joint_color = list(map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num]))
                    else:
                        joint_color = map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num])

                    cv2.circle(test_img, center=(joint_coord[1], joint_coord[0]), radius=3, color=joint_color, thickness=-1)
                else:
                    if PYTHON_VERSION == 3:
                        joint_color = list(map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num]))
                    else:
                        joint_color = map(lambda x: x + 35 * (joint_num % 4), joint_color_code[color_code_num])

                    cv2.circle(test_img, center=(joint_coord[1], joint_coord[0]), radius=3, color=joint_color, thickness=-1)
        print('plot joint time %f' % (time.time() - t1))

        return test_img

if __name__ == '__main__':
    start = time.time()    
    inst = CpmClass()
    print('Initialization took %.02f secs'%(time.time()-start))

    start = time.time()
    # tf.app.run(main = inst.run)
    inst.run()

import numpy as np
from scipy import signal, ndimage, spatial

import cv2
import time
from threading import Thread


laplace = np.array([
    [0,-1,0],
    [-1,4.,-1],
    [0,-1,0]
    ])

gaussian = np.array([
    [0.102059,  0.115349,   0.102059],
    [0.115349,  0.130371,   0.115349],
    [0.102059,  0.115349,   0.102059]
    ])


LoG = signal.convolve2d(gaussian, laplace)


WIDTH = 640
HEIGHT = 360
DIM = (HEIGHT, WIDTH)

"""
Prepare an image for sensor comparisons
"""
def prepareImage(frame):
    global LoG, laplace, sobel, sharr

    # resize image
    # frame = cv2.resize(frame, DIM, interpolation = cv2.INTER_AREA)
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # grayFrame = frame[:,:,2]
    # grayFrame = frame
    # create a CLAHE object (Arguments are optional).
    # clahe = cv2.createCLAHE(clipLimit=0, tileGridSize=(4,4))
    # grayFrame = clahe.apply(grayFrame)

    # grayFrame = cv2.filter2D(grayFrame, -1, laplace)

    # a = cv2.GaussianBlur(grayFrame,(9,9),0.7)
    # b = cv2.GaussianBlur(grayFrame,(9,9),4)
    # grayFrame = a - b
    # grayFrame = np.abs(b - a)
    # grayFrame = cv2.GaussianBlur(grayFrame,(9,9),1.5)
    # grayFrame = grayFrame - np.min(grayFrame)
    # grayFrame = ( (grayFrame.astype(np.float) / np.max(grayFrame.astype(np.float))) * 255.0 ).astype(np.uint8) 
    return grayFrame

def difference(live, reference):
    # diff = cv2.subtract(reference, live)
    diff = cv2.subtract(live, reference)
    # diff = np.abs(live.astype(np.float) - reference.astype(np.float))
    # diff[diff < 20] = 0
    # diff[diff > 0] = 255
    # diff[diff < 35] = 0
    # # # # diff = (diff / np.max(diff)) * 255.0
    # diff[diff > 0] = 255
    # kernel = np.ones((3,3),np.uint8)
    # diff = cv2.erode(diff,kernel,iterations = 1)
    # print('Max', np.max(diff))
    # # diff = cv2.threshold(diff,127,255,cv2.THRESH_BINARY)
    # kernel = np.ones((3,3),np.uint8)
    # diff = cv2.dilate(diff,kernel,iterations = 1)
    # blur = cv2.GaussianBlur(diff,(9,9),10)
    # diff = cv2.adaptiveThreshold(diff,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,2)

    return diff.astype(np.uint8) 


class Camera:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True



# mask is the mask so far, 
# add another circle to the mask
def maskPoint(currentMask, x, y, r):
    currentMask[y-r:y+r, x-r:x+r] = 1
    return currentMask

# Take colour image and crop a b&w bit out of it
def crop(image, mask):
    # c = image[mask>0]
    c = image[mask]
    # c = c - np.min(c)
    # c = c / np.max(c)
    # print('Crop', image.shape, c.shape)
    return c
    
def similarity(a,b):
    return cv2.PSNR(a, b)

import numpy as np
import json
import cv2
import time
import math
from threading import Thread


WIDTH = 1280
HEIGHT = 720
# WIDTH = 640
# HEIGHT = 360

IMAGE_SHAPE = (HEIGHT, WIDTH)
RESIZE_DIM = (WIDTH, HEIGHT)

controls = [
    {"name": "blur-1", "min":-1, "max":40, "step":2},
    {"name": "blur-3", "min":1, "max":40, "step":2},
    {"name": "diff-threshold", "min":1, "max": 255, "step": 1},
    {"name": "diff-blur", "min":1, "max": 30, "step": 2},
    {"name": "diff-percent", "min": 0, "max": 1, "step": 0.01},
    {"name": "scharr-min", "min": 0, "max": 10 , "step": 0.01},
    {"name": "scharr-max", "min": 0, "max": 10, "step": 0.01},

]   

values = {}
n = 1
for x in controls:
    x['control'] = n
    n = n + 1
    values[x['name']] = 0

# values["blur-3"] = 5
# values["diff-threshold"] = 53 #50
# values["DoG-Sigma-1"] = 1.91
# values["DoG-Grid-Size-1"] = 13
# values["DoG-Sigma-2"] = 1.97
# values["DoG-Grid-Size-2"] = 13
# values["diff-blur"] = 9
# values["blur-3"] = 3
# values["diff-threshold"] = 36
# values["diff-blur"] = 13
values["blur-3"] = 3
values["diff-threshold"] = 36
values["diff-blur"] = 13
values["blur-3"] = 3
values["diff-threshold"] = 40
values["diff-blur"] = 9

values["blur-1"] = -1
values["diff-threshold"] = 73
values["diff-blur"] = 17
values["blur-3"] = 5
values["scharr-min"] = 3.34
values["scharr-max"] = 8.79

print(values)


DEV_MODE = False






"""
Prepare an image for sensor comparisons
"""
def prepareImage(frame):


    # src = cv2.resize(frame, RESIZE_DIM)
    src = frame
    grayFrame = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)


    # DOG
    # s1 = int(values["DoG-Grid-Size-1"])
    # s2 = int(values["DoG-Grid-Size-2"])
    # sigma1 = float(values["DoG-Sigma-1"])
    # sigma2 = float(values["DoG-Sigma-2"])
    # blur1 = cv2.GaussianBlur(grayFrame, (s1,s1), sigma1, borderType=cv2.BORDER_REPLICATE)
    # blur2 = cv2.GaussianBlur(grayFrame, (s2,s2), sigma2, borderType=cv2.BORDER_REPLICATE)
    # img_dog2 = blur1 - blur2
    # img_dog2 = (img_dog2).clip(0,255).astype('uint8')
    # grayFrame = img_dog2

    if ( int(values["blur-1"]) > 0 ):
        grayFrame = cv2.GaussianBlur(grayFrame, (int(values["blur-1"]),int(values["blur-1"])), 0)

    # return grayFrame

    l = float(values['scharr-min'])
    h = float(values['scharr-max'])

    scharr_X = np.array([
        [-l, 0, l],
        [-h, 0, h],
        [-l, 0, l]
    ])

    scharr_Y = np.array([
        [-l, -h, -l],
        [0, 0, 0],
        [l, h, l]
    ])

    # The above two can be added to produce this which gives the same result as running
    # each of the above and summing the outputs
    scharr = scharr_X + scharr_Y

    # # grayFrame = cv2.blur(grayFrame, (int(values['blur-1']),int(values['blur-1']))).astype(np.float32)
    # # # Scharr
    grayFrame = cv2.filter2D(grayFrame, -1, scharr)

    # grayFrame = cv2.blur(grayFrame, (int(values['blur-3']),int(values['blur-3'])))

    # grayFrame = grayFrame.astype(np.uint8)
 
    # grayFrame = cv2.Laplacian(grayFrame,cv2.CV_64F)

    # # 3x3 Y-direction  kernel
    # sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    # # 3 X 3 X-direction kernel
    # sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    # # Filter the image using filter2D, which has inputs: (grayscale image, bit-depth, kernel)
    # grad_y = cv2.filter2D(grayFrame.astype(np.float32), -1, sobel_y)
    # grad_x = cv2.filter2D(grayFrame.astype(np.float32), -1, sobel_x)
    # scale = 0.2
    # delta = 0
    # ddepth = cv2.CV_32F

    # gray = grayFrame
    
    # grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    # grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    
    # # # phase = cv2.phase(grad_x, grad_y, angleInDegrees = True) * 255.0/360
    # magnitude = cv2.magnitude(grad_x, grad_y)  
    # grayFrame = magnitude 
    # grayFrame = magnitude.astype(np.uint8)

        
    # grayFrame = cv2.filter2D(grayFrame.astype(np.float32), -1, scharr).astype(np.uint8)

    # gray = cv2.blur(gray, (int(values["blur-3"]),int(values["blur-3"])))
    
    if ( int(values["blur-3"]) > 0 ):   
       grayFrame = cv2.GaussianBlur(grayFrame, (int(values["blur-3"]),int(values["blur-3"])), 0)

    # if ( int(values["threshold"]) > 0 ):
    #     _, grayFrame = cv2.threshold(grayFrame, int(values["threshold"]), 255, cv2.THRESH_BINARY)
    
    # if ( int(values["erode"]) > 0 ):
    #     kernel = np.ones((int(values["erode"]), int(values["erode"])),np.uint8)
    #     grayFrame = cv2.erode(grayFrame,kernel,iterations = 1)


    return grayFrame


def difference(live, reference):
    diff = cv2.absdiff(live, reference)
    diff = cv2.GaussianBlur(diff, (int(values["diff-blur"]),int(values["diff-blur"])), 0)
    _, diff = cv2.threshold(diff, int(values["diff-threshold"]), 255, cv2.THRESH_BINARY)
    return diff


# mask is the mask so far, 
# add another circle to the mask
def maskPoint(currentMask, x, y, r):
    currentMask[y-r:y+r, x-r:x+r] = 1
    return currentMask

# Take colour image and crop a b&w bit out of it
def crop(image, mask):
    c = image[mask]
    return c
    
def scoreSubImageSimilarity(thresholded):
    return cv2.countNonZero(thresholded)

def similarity(a,b):
    return cv2.PSNR(a, b)

def keepCommon(a,b):
    return cv2.addWeighted(a, 0.5, b, 0.5, 0)






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
            # self.frame = cv2.resize(self.frame, RESIZE_DIM)

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True













def developerControl(name, value):
    global values
    if ( DEV_MODE ):
        print("Setting", name, value)
        for c in controls:
            # print("Control", 'slider' + str(c['control']), c['name'])
            if ( name == 'slider' + str(c['control']) ):
                # value is between 0 and 100
                values[c['name']] = value
        print("Developer controls", values)



"""
==============================================================================================
MQTT - Server is assumed to be running locally.  Subscribe to events from the web app
       such as requests to renew configuration or save a screenshot
==============================================================================================
"""
import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("MQTT broker connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/Developer/#")

def on_message(client, userdata, msg):
    global saveNextFrame, monitorSensor, timing, timingP, exitCurrentLoop
    # print("My Lib", msg.topic)
    if ( "/Developer/" in msg.topic ):
        # print("Developer Payload", "[" + str(msg.payload) + "]")
        # print(msg.topic.split('/Developer/')[1], int(msg.payload))
        name = msg.topic.split('/Developer/')[1]
        value = float(msg.payload)
        developerControl(name, value)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, keepalive=10000)

client.loop_start(); # Place a thread in the background to read the incoming traffic and wait if necessary

s = json.dumps(controls)
ret = client.publish("/DeveloperControl", s, retain=True);

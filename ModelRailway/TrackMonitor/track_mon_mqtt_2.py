'''

Track Monitor

By David Goddard 2021


'''

import json
from scipy import signal, ndimage, spatial
from scipy import misc
from skimage.transform import resize
import numpy as np
import time
import datetime
from os import listdir
from os.path import isfile, join
import cv2
import matplotlib.pyplot as plt
import copy
import sys, getopt
import my_lib

REF_FOLDER = './ref/'

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
    client.subscribe("/TrackMonitor/webapp/#")

# The callback for when a PUBLISH message is received from the server.
saveNextFrame = None
monitorSensor = None
exitCurrentLoop = False

timing = []
timingP = 0


def on_message(client, userdata, msg):
    global saveNextFrame, monitorSensor, timing, timingP, exitCurrentLoop
    print(msg.topic)
    if ( msg.topic == "/TrackMonitor/webapp/snapshot" ):
        print("Payload", "[" + str(msg.payload) + "]")
        if ( msg.payload == b'save'):
            print("Request to save a snapshot!")
            saveNextFrame = REF_FOLDER + datetime.datetime.now().strftime("reference_%Y%m%d%H%M%S.png");
    if ( "/monitor/" in msg.topic ):
        print("Payload", "[" + str(msg.payload) + "]")
        bits = msg.topic.split('/monitor/')
        print(bits)
        sensor = int(bits[1])
        print("Request to monitor a sensor")
        monitorSensor = sensor
        timing = []
        timingP = 0
    if ( "/config/" in msg.topic ):
        exitCurrentLoop = True


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, keepalive=10000)

client.loop_start(); # Place a thread in the background to read the incoming traffic and wait if necessary




# initialize the camera 

vs = my_lib.Camera(src=0).start()

stats = np.zeros(100)
statsPtr = 0
currentRef = None
currentRefScore = -1

while ( True ):
    print("Initialising with current config")

    # Load POI information

    POI = []

    with open('POI.json') as json_file:
        POI = json.load(json_file)

    # Load all reference images and extract their POI ready to compare
    # Index by POI ID

    POI_MASK = {}
    for p in POI['POI']:
        ID = p['id']
        p['state_changed'] = 0
        p['initialised'] = False

        mask = np.zeros(my_lib.IMAGE_SHAPE)
        
        # create mask of all points in this sensor

        for xy in p['points']:

            # add to the mask as required

            h = my_lib.HEIGHT
            w = my_lib.WIDTH
            mask = my_lib.maskPoint(mask, int(w * float(xy[0])), int(h * float(xy[1])), p['radius'])

        mask = mask.reshape((h*w))
        POI_MASK[ID] = np.asarray(np.where(mask > 0))

    REF_PRE_PROCESSED = []
    REF_MASK = {}
    REF_IMAGE = []
    REF_SIZE = (10,10)

    onlyfiles = sorted([join(REF_FOLDER, f) for f in listdir(REF_FOLDER) if isfile(join(REF_FOLDER, f) )])
    fileCount = -1
    for file in onlyfiles:
        fileCount = fileCount + 1
        print(file)
        frame = cv2.imread(file)
        REF_IMAGE.append(cv2.resize(frame, REF_SIZE))
        frame = my_lib.prepareImage(frame)
        REF_PRE_PROCESSED.append(np.copy(frame))
        h = my_lib.HEIGHT
        w = my_lib.WIDTH
        frame = frame.reshape((h*w))
        REF_MASK[fileCount] = {}
        for p in POI['POI']:
            ID = p['id']
            REF_MASK[fileCount][ID] = frame[POI_MASK[ID]]
            
    if ( len(REF_PRE_PROCESSED) == 0):
        saveNextFrame = REF_FOLDER + datetime.datetime.now().strftime("reference_%Y%m%d%H%M%S.png");

    print("All reference items now loaded")     


    startTime = datetime.datetime.now()

    # capture frames from the camera
    frameNum = 0

    # Load image from camera and compare to each ref image.
    tic = time.perf_counter()

    while ( not exitCurrentLoop):
        frame = vs.read()

        # Save image if requested
        """
        ==============================================================================================
        Get a new reference image

        MQTT message - /TrackMonitor/webapp/snapshot

        This will take a screenshot and save it to disk
        ==============================================================================================
        """
        if ( saveNextFrame != None ):
            cv2.imwrite(saveNextFrame, frame)
            ret = client.publish("/TrackMonitor/webapp/saved", saveNextFrame);
            print("Send image: " + saveNextFrame)
            saveNextFrame = None
            exitCurrentLoop = True

        else:
            frameForRef = cv2.resize(frame, REF_SIZE)
     
            edges = my_lib.prepareImage(frame)  # from camera feed

            # Work out best reference image to use

            useRef = 0
            bestRefScore = -1
            for r in range(len(REF_IMAGE)):
                s = my_lib.similarity(frameForRef, REF_IMAGE[r])
                if ( bestRefScore < s ):
                    bestRefScore = s
                    useRef = r  
            if ( useRef != currentRef ):
                print("Using ref image", useRef)
                ret = client.publish("/TrackMonitor/track/reference/id", str(useRef), retain=True);
                currentRef = useRef
                currentRefScore = bestRefScore

            # Compare sensor points with the same ones in the reference image
            diff = my_lib.difference(edges, REF_PRE_PROCESSED[useRef])

            stack = np.hstack([diff, edges])
            # cv2.imwrite('example_diff.png', diff)
            # cv2.imwrite('example_edges.png', edges)
            # cv2.namedWindow("main", cv2.WINDOW_NORMAL)
            # cv2.resizeWindow("main", 1200, 600)
            # cv2.imshow("main",stack)
            # if(cv2.waitKey(1) & 0xFF == ord('q')):
            #     vs.stop()
            #     cv2.destroyAllWindows()


            diff.shape = (diff.shape[0] * diff.shape[1])

            for sensorIdx in range(len(POI['POI'])):
                sensor = POI['POI'][sensorIdx]
                ID = sensor['id']
                
                triggerLevel = int(sensor['sensitivity'])   # **2 #float(sensor['sensitivity'])
                lastState = int(sensor['state'])
                sensorState = 0

                mask = POI_MASK[ID]
                score = my_lib.scoreSubImageSimilarity(diff[mask])
                # print("Sensor", ID, "score", score)

                # sensorHistory[ID, sensorHistoryIdx] = score
                # score = np.median(sensorHistory[ID])

                if ( score > triggerLevel ):
                    sensorState = 1

                if ( monitorSensor != None and monitorSensor == ID ):
                    timing.append(str(sensorState) + '|' + str(score))
                    timingP += 1
                    if ( timingP > 10 ):
                        timingP = 0
                        ret = client.publish("/TrackMonitor/webapp/monitorResult", (",".join(timing)) )# str(int(bestSensorMatch)));
                        timing = []
                

                changedState = lastState != sensorState
                sensor['state'] = int(sensorState)

                if ( (sensor['initialised'] == False) or changedState ):
                    sensor['initialised'] = True
                    sensor['state_changed'] = time.perf_counter()

                    # notify MQTT server
                    if ( sensorState == 1 ):
                        ret = client.publish("/TrackMonitor/track/sensor/" + str(ID),"ACTIVE", retain=True);
                        print("---------------------------- Sensor " + str(ID) + " Triggered with score ", score)
                    else: 
                        ret = client.publish("/TrackMonitor/track/sensor/" + str(ID),"INACTIVE", retain=True);
                        print("---------------------------- Sensor " + str(ID) + " Cleared with score ", score)

        toc = time.perf_counter()
        stats[statsPtr] = (toc - tic)
        statsPtr = statsPtr + 1
        if ( statsPtr > stats.shape[0] - 1):
            statsPtr = 0
            print("Average frame processing time: %0.3f seconds" % np.median(stats) )
        tic = time.perf_counter()



    exitCurrentLoop = False





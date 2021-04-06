"""
Simple test utility which runs the same code as the main detector for
processing the image ready for scanning sensor locations.

This is used to help align the camera 
"""

import numpy as np
import cv2
import time
import my_lib
from os import listdir
from os.path import isfile, join
import sys

REF_FOLDER = './ref/'
REF_IMAGE = []
REF_FOR_COMPARE = []

onlyfiles = sorted([join(REF_FOLDER, f) for f in listdir(REF_FOLDER) if isfile(join(REF_FOLDER, f) )])
fileCount = 0
refImage = None
for file in onlyfiles:
    fileCount = fileCount + 1
    refImage = cv2.imread(file)
    REF_FOR_COMPARE.append(np.copy(cv2.resize(refImage, (10,10))))
    refImage = cv2.resize(refImage, my_lib.RESIZE_DIM)
    REF_IMAGE.append(np.copy(refImage))



vs = my_lib.Camera(src=0).start()


currentRef = -1

while(True):
    try:
        tic1 = time.perf_counter()



        fromCamera = vs.read()
        forCompare = cv2.resize(fromCamera, (10,10))
        fromCamera = cv2.resize(fromCamera, my_lib.RESIZE_DIM)

        useRef = 0
        bestRefScore = -1
        for ri in range(len(REF_FOR_COMPARE)):
            x = REF_FOR_COMPARE[ri]
            s = my_lib.similarity(forCompare, x)
            if ( bestRefScore < s ):
                bestRefScore = s
                useRef = ri
        if ( useRef != currentRef ):
            ret = my_lib.client.publish("/TrackMonitor/track/reference/id", str(useRef), retain=True);
            currentRef = useRef
            currentRefScore = bestRefScore

        print("Using ref image: ", useRef)
        r = my_lib.prepareImage(REF_IMAGE[useRef])
        frame = my_lib.prepareImage(fromCamera)


        # fromCamera = cv2.cvtColor(fromCamera, cv2.COLOR_BGR2GRAY)

        toc = time.perf_counter()
        print(f"Frame {toc - tic1:0.4f} Seconds")

        tic1 = time.perf_counter()
        diff = my_lib.difference(frame, r)
        # diff = cv2.addWeighted(frame,0.1,diff,0.9,0)
        toc = time.perf_counter()

        print(f"  Subtraction {toc - tic1:0.4f} Seconds")

        stack = np.hstack([frame, r, diff])
        cv2.namedWindow("main", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("main", 1200, 600)
        cv2.imshow("main",stack)
        if(cv2.waitKey(1) & 0xFF == ord('q')):
            vs.stop()
            cv2.destroyAllWindows()
    except KeyboardInterrupt:
        vs.stop()
        cv2.destroyAllWindows()
        sys.exit()
    # except Exception as e: # work on python 3.x
    #     print('Failed  '+ str(e))



"""
Simple test utility which runs the same code as the main detector for
processing the image ready for scanning sensor locations.

This is used to help align the camera 
"""

import numpy as np
import cv2
from scipy import signal
import time
import my_lib
from os import listdir
from os.path import isfile, join

ID = 2

REF_FOLDER = './ref/'
onlyfiles = sorted([join(REF_FOLDER, f) for f in listdir(REF_FOLDER) if isfile(join(REF_FOLDER, f) )])
fileCount = 0
refImage = None
for file in onlyfiles:
    fileCount = fileCount + 1
    if ( fileCount == ID ):
        print(file)
        refImage = cv2.imread(file)
        refImage = my_lib.prepareImage(refImage)

vs = my_lib.Camera(src=0).start()


while(True):
    tic1 = time.perf_counter()
    frame = vs.read()


    # resize image
    frame = my_lib.prepareImage(frame)


    diff = my_lib.difference(frame, refImage)

    stack = np.hstack([frame, refImage, diff])
    cv2.imshow('Capturing Video',stack)
    if(cv2.waitKey(1) & 0xFF == ord('q')):
        vs.stop()
        cv2.destroyAllWindows()
    toc = time.perf_counter()
    print(f"Frame {toc - tic1:0.4f} Seconds")


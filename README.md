# Track Monitor
A Block occupancy and location sensor for small model railways using only a Raspberry Pi model 3 or later and a webcam or Raspberry Pi Camera module.

[See app running alongside the JMRI sensors page](https://www.youtube.com/watch?v=h2c3jTDoKAY)


The software is split into two parts:
  * A python based application which takes images using the webcam and combines these with user-defined sensor locations and block locations and generates MQTT messages indicating their state.  A suitably configured JMRI system capable of using MQTT messages can be configured to respond to these sensors as the locomotives move around the track and it requires no additional wiring, no cutting tracks, no additional resistors being attached to rolling stock etc.
  * A NodeJS server hosting a simple web site containing two web pages:  One to capture reference images and one to enable a user to define the sensor locations.

# Setup and Use
[Refer to the Instructables site for more information.](https://www.instructables.com/Block-Occupancy-Detector-and-Position-Sensors-for-/)

# Example

[Video showing live action on a demonstration model railway](https://youtu.be/tM7jrEE13So)

a picture showing on the left: the live feed, in the middle: the reference image and on the right: the differences.  There are three locomotives on the track as per the video; one at nearly 12 o’clock, one around 4 o’clock and the last one around 7 o’clock.  There are other changes being picked out as I have put or moved stuff from around the layout which is accounting for a lot of the other noise but those bits do not overlap with any virtual sensor I have setup it does not matter.

The reference image was taken with nothing on the track and there are lots of versions of this under different lighting - about 10 images in all including side lighting only, overhead lighting only, combined, daylight, sunlight etc.

You can see that the difference image is less than perfect (not perfect outlines of the trains) but all it needs is a few white pixels in order to trigger.

	[Comparing images](https://github.com/davidgoddard/track-monitor/blob/main/example1.png)

Below is the a video clip showing the web page view which shows the background reference image change due to changes in lighting but the detected train locations is not affected.

	[Showing lighting changes](https://github.com/davidgoddard/track-monitor/blob/main/example2.mov)


The images from the camera are converted to black and white, blurred and then run through a ‘scharr’ filter which is a pair of 3x3 matrices; one for vertical changes and the other for horizontal changes.  This results in the edges of the track standing out and causing where the train to ‘look different’ and by subtracting the two images you are left with the differences.

I can get better results but not as fast.  This version takes around 60ms to grab a frame off the camera, process it, detect all the points I’m interested in and broadcast over MQTT which sensors are currently being triggered - not bad for a Raspberry Pi model 3 costing around 30 quid!
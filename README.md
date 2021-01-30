# Track Monitor
A Block occupancy and location sensor for small model railways using only a Raspberry Pi model 3 or later and a webcam or Raspberry Pi Camera module.

[See app running alongside the JMRI sensors page](https://www.youtube.com/watch?v=h2c3jTDoKAY)


The software is split into two parts:
  * A python based application which takes images using the webcam and combines these with user-defined sensor locations and block locations and generates MQTT messages indicating their state.  A suitably configured JMRI system capable of using MQTT messages can be configured to respond to these sensors as the locomotives move around the track and it requires no additional wiring, no cutting tracks, no additional resistors being attached to rolling stock etc.
  * A NodeJS server hosting a simple web site containing two web pages:  One to capture reference images and one to enable a user to define the sensor locations.

# Setup and Use
Refer to the Instructables site for more information.


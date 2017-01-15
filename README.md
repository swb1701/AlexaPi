# AlexaPi
Code for a Pi-based Alexa Supplement

This demonstration runs on a Raspberry Pi 3 (or could run on any Pi with bluetooth and wifi).
It utilizes a PiTFT shield providing a display and a Pi camera to take photos.

The Pi is bluetooth paired with the Amazon Echo speaker.  An Alexa skill can then provide interaction
with the Pi and the Pi can speak from the Echo speaker.  The Pi uses AWS Polly to provide text to speech.
A long-polled AWS SQS queue provides the input to the Pi.  The Alexa skill activates an AWS Lambda script
(also in Python) which queues JSON on SQS for the Pi to execute.  

Among other things, this approach allows spoken notifications on the Amazon Echo from Lambda.

The demo focuses on the AWS Rekognition API and lets the Pi enroll new users and recognize them in response
to spoken commands to the Echo.

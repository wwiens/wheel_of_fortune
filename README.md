# Wheel of Fortune Puzzle Detector

**THIS IS A WORK-IN-PROGRESS** *This project is not fully complete, but I am sharing it because there is a lot of working code here that could be useful.*

As a regular fan of Wheel of Fortune, I often find myself wishing for a way to see all the letters that have been guessed for a puzzle. The correct ones are visible, but there is no way to see the guesses that were incorrect. Computer vision seemed like a good way to solve this. After a few weeks of training and coding, I am excited to share a project that does exactly that.
[image - WOF screen and Puzzle Board]

It uses a USB HDMI capture device connected to a Roku express to capture images from the show while it is being aired. This serves two purposes. It allowed me to capture images from the show to use for training and is also how I grab images to send for inference to detect letters.

Training the computer vision models was the biggest part of the project. I have shared the datasets and models that were created for this on Roboflow. There are two separate datasets and models. These are:

Wheel of Fortune Puzzle Board
https://universe.roboflow.com/warren-wiens-d0d4p/wheel-of-fortune

Wheel of Fortune Call Letters
https://universe.roboflow.com/warren-wiens-d0d4p/wheel-of-fortune-call-letters

## Project Overview
The project consists of two main sections. The first is a set of Python scripts that wil lgenerate the puzzle board images needed for the machine learning training. These not only create the images, they also create the annotation files at the same time. 

The other section is the web page that displays a puzzle board and the call letters. It uses Socket.IO to update the board and the call letters in real time as the script retrieves images from the video feed and sends to a local instance of a Roboflow inference server.


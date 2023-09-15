import json
import requests
import cv2
import base64
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
from string import Template
from collections import Counter
import time

# Set logging flag - will log data to a JSON file for troubleshooting
logging = False
logfile = "log" + time.strftime("%Y%m%d-%H%M%S") + ".json"

# Define the URLS to use for inference 
puzzleurl = "http://127.0.0.1:9001/wheel-of-fortune/1?api_key=YOUR-API-KEY-GOES-HERE"
url = "http://127.0.0.1:9001/wheel-of-fortune-call-letters/1?api_key=YOUR-API-KEY-GOES-HERE"

# desired row and column values - we want to translate the incoming box dimensions to these values
row = [80,120,160,195,230,265,300,335,370,405,445,480,515,550]
col = [155,215,270,325]

# Define a dictionary to store the letters that are called and their appearances - we will count them
# so we are not faslely triggering on a single letter
call_letters = {}
call_letters['A'] = 1
lastcall = ""

# Define a variable for the confidence threshold
confidence = 0.8

# Connect to video and set resolution - note that the camera number may chance for your setup
vid = cv2.VideoCapture(0)

# Initialize the Flask app and socketio
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

thread = None
thread_lock = Lock()

# Define path for the index page
@app.route('/')
def index():
    return render_template('index.html')

# PRint message when client connects 
@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(update_puzzle)

# Print message when client disconnects
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

def getpredictions(response):
    # This function will filter the results from the inference server to only return results with a confidence
    # greater than the threshold and return them in a list
    result = []
    for prediction in response:
        if prediction['confidence'] > .8:
            x = prediction['x']
            y = prediction['y']
            class_ = prediction['class']
            result.append([x, y, class_])
            
    return result

def normalizepredictions(listtonormalize):
    # This function changes the box coordinates to match the ones in our Col and Row lists
    modifiedList = [(min(row, key=lambda x: abs(x - item[0])), item[1], item[2]) for item in listtonormalize]
    modifiedList = [(min(col, key=lambda x: abs(x - item[1])), item[0], item[2]) for item in modifiedList]
    return modifiedList

def letterstring(listtonormalize):
    # This function converts the list of letters to a string that will be passed to the browser
    strLetters = ""
    for c in col:
        for r in row:
            result = [inner_list for inner_list in listtonormalize if inner_list[1] == r and inner_list[0] == c]
            if len(result) > 0:
                str = result[0][2]
                if str == "SP":
                    strLetters += "#"
                elif str == "DA":
                    strLetters += "-"            
                elif str == "AP":
                    strLetters += "'"    
                elif str == "AM":
                    strLetters += "&"                        
                elif str == "EX":
                    strLetters += "!"                                            
                else:
                    strLetters += str
            else:
                strLetters += "_"
    return strLetters

def checkcallletters(letter):
    # This function tracks what call letters have been guessed
    global call_letters
    global lastcall

    if letter.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and len(letter) == 1:
        if letter in call_letters.keys():
            call_letters[letter] = call_letters[letter] + 1
        else:
            call_letters[letter] = 1

        strCall = ""
        for x, y in call_letters.items():
            if y > 10:
                if x not in strCall:
                    strCall += x

        if lastcall != strCall:
            calldata = { 'call_letters': strCall }
            socketio.emit('callletter', calldata)

        lastcall = strCall

def checkpuzzlereset(letterlist):
    # This function resets the puzzle
    # It does this by checking the number of letters and blanks - if there are more than 7 letters and no blanks
    # we assume a completed puzzle and reset
    blanks = 0
    letters = 0
    tiles = 0
    for x in letterlist:
        if x == "#":
            blanks += 1
        elif x == "_":
            tiles += 1
        else:
            letters += 1
    
    if letters > 7 and blanks == 0:
        return True
    else:
        return False


# Main loop to process the video stream and send image to inference server for processing
def update_puzzle():

    if logging:
        fileout = open(logfile, "w")

    # Define variables for the change detection section
    letterlist = ["_"] * 56
    lettercount = [0] * 56

    while(True):
        ret, frame = vid.read()

        # Check for call letters
        # Crop to 250x250
        x, w, y, h = 0, 250, 230, 250
        crop_img = frame[y:y+h, x:x+w]
        ret, buffer = cv2.imencode('.jpg', crop_img)

        # Convert to base64 string
        img_str = base64.b64encode(buffer)

        # Define the headers and send the image to the inference server
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=img_str, headers=headers)

        # Get the results and check the confidence level
        response = response.json()['predictions']
        if response:
            if response[0]['confidence'] > 0.9:
                checkcallletters(response[0]['class'])
            if logging:
                timedate = [{"time": str(datetime.now()),"type": "call"}]
                jsonout = timedate + response
                json.dump(jsonout, fileout, ensure_ascii=False, indent=4)                

        # Same as above, but for the puzzle board
        ret, buffer = cv2.imencode('.jpg', frame) 
        img_str = base64.b64encode(buffer)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(puzzleurl, data=img_str, headers=headers)
        
        # Get the resultsl
        response = response.json()['predictions']
        if response and logging:
            timedate = [{"time": str(datetime.now()),"type": "puzzle"}]
            jsonout = timedate + response
            json.dump(jsonout, fileout, ensure_ascii=False, indent=4)   

        predictions = getpredictions(response)

        # The following function is how we map letter positions to the real positions on the puzzle board
        # as the bounding box results won't be exact
        normalized = normalizepredictions(predictions)

        # Sort the list by the y value first, then the x value - this should match the order of the puzzle board
        sorted_list = sorted(normalized, key=lambda x: (x[1], x[0]))

        # This converts the list of letters to a string that will be passwed to the browser
        puzzleletters = letterstring(sorted_list)
        if logging:
            jsonout = [{"time": str(datetime.now()),"type": "board", "letters": puzzleletters}]
            json.dump(jsonout, fileout, ensure_ascii=False, indent=4)          

        # This section is for change detection - it will only send the string to the browser if there is a change           
        changeflag = 0
        for letter in range(0, 56):
            
            if Counter(puzzleletters)['_'] < 46:
                 # Initial assignment
                if  puzzleletters[letter] != letterlist[letter] and lettercount[letter] == 0:
                    if letterlist[letter] == "#" and puzzleletters[letter] == "_":
                        lettercount[letter] = lettercount[letter]
                    else:
                        letterlist[letter] = puzzleletters[letter]
                        lettercount[letter] =  1
                        changeflag = 1
                    
                # If the character is the same as the last line - increment the counter
                elif puzzleletters[letter] == letterlist[letter] and lettercount[letter] != 0:
                    lettercount[letter] = lettercount[letter] + 1
                
                # If the character is different than the last line - decrement the counter
                elif puzzleletters[letter] != letterlist[letter] and lettercount[letter] >= 0:
                    lettercount[letter] = lettercount[letter] - 1

                if letterlist[letter] == "#" and lettercount[letter] > 10:
                    lettercount[letter] = 10

        # If there was a change, send the string to the browser
        if changeflag == 1:
            if checkpuzzlereset(letterlist):
                print("Resetting puzzle")
                time.sleep(2)
                letterlist = ["_"] * 56
                lettercount = [0] * 56
                changeflag = 0                

            board = { 
                'row1': letterlist[0:14],
                'row2': letterlist[14:28],
                'row3': letterlist[28:42],
                'row4': letterlist[42:56]
            }

            # Sends the puzzle data to the browser
            socketio.emit('puzzle', board)


if __name__ == '__main__':
    socketio.run(app)
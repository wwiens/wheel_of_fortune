# Generates simulated WoF puzzle boards based on the
# phrases in PHRASES.txt. Each phrase will be placed
# as tiles on the puzzle board and saved as a new image
# An annotation file will also be generated for each
# puzzle board, based on where each letter was placed.

# FOLDERS


import cv2
import uuid
import random
import os

mystring = """
<annotation>
	<folder></folder>
	<filename>$filename$</filename>
	<path>$filename$</path>
	<source>
		<database>WheelBot</database>
	</source>
	<size>
		<width>570</width>
		<height>300</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
"""

myobject = """
	<object>
		<name>$name$</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<occluded>0</occluded>
		<bndbox>
			<xmin>$xmin$</xmin>
			<xmax>$xmax$</xmax>
			<ymin>$ymin$</ymin>
			<ymax>$ymax$</ymax>
		</bndbox>
	</object>
"""
boundingbox = ""
objectboundaries = ""


def split_sentence(sentence):
    # This functions converts a sentence into 4 rows that match the puzzle board
    words = sentence.split()  # Split the sentence into individual words
    rows = []  # List to store the rows
    board = [13,15,15,13]
    boardrow = 0
    curr_row = ""  # Current row being constructed
    for word in words:

        if len(curr_row) + len(word) + 1 <= board[boardrow]:
            curr_row += word + " "  # Add the word to the current row
        else:
            rows.append(curr_row)  # Add the current row to the rows list
            curr_row = word + " "  # Start a new row with the current word
            boardrow += 1
    rows.append(curr_row)  # Add the last row to the rows list
    return rows


def add_image (baseimg, newimg, col, row, char):
    # Get the height and width of the small image
    global objectboundaries
    small_height, small_width, _ = newimg.shape
    x_offset = x_vals[col]
    y_offset = y_vals[row]
    baseimg[y_offset:y_offset + small_height, x_offset:x_offset + small_width] = newimg
    boundingbox = myobject
    boundingbox = boundingbox.replace("$xmin$", str(x_offset))
    boundingbox = boundingbox.replace("$xmax$", str(x_offset+37))
    boundingbox = boundingbox.replace("$ymin$", str(y_offset))
    boundingbox = boundingbox.replace("$ymax$", str(y_offset+55))
    boundingbox = boundingbox.replace("$name$", str(char))
    if char != "TL":
        objectboundaries += boundingbox
    return baseimg


def charToString(char):
    string = ""
    for x in char:
        string += x
    return string

def write_row (baseimg, phrase, row, start, rowsize):
    phrase = phrase.rstrip()
    phrase = phrase.replace("\t", "")
    letterpos = start
    if start == 0:
        letterpos = rowsize - len(phrase)
        letterpos = int(letterpos / 2)
    for char in phrase.lower():
        if char == " ":
            newimg = tl_image
            class_name = "TL"
        elif char == "?":
            newimg = qu_image   
            class_name = "QU" 
        elif char == "!":
            newimg = ex_image 
            class_name = "EX"   
        elif char == "'":
            newimg = ap_image
            class_name = "AP"   
        elif char == "-":
            newimg = da_image
            class_name = "DA" 
        elif char == "&":
            newimg = am_image 
            class_name = "AM"                        
        elif char in "abcdefghijklmnopqrstuvwxyz":
            newimg = globals()[char + "_image"]
            class_name = char.upper()
        else:
            newimg = tl_image
        if random.randint(1, 5) == 3:
            newimg = sp_image
            class_name = "SP"
        baseimg = add_image(baseimg, newimg, letterpos, row, class_name)
        letterpos += 1

    return baseimg


# Define X and Y values for bounding boix positions
x_vals = [5, 45, 85, 125, 165, 205, 245, 285, 325, 365, 405, 445, 485, 525]
y_vals = [3, 63, 122, 181]

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O','P','Q','R','S','T','U','V','W','X','Y','Z']

tile_width = 37
tile_height = 54

backgrounds = []
backgrounds.append('largeback/L1.jpg')
backgrounds.append('largeback/L2.jpg')
backgrounds.append('largeback/L3.jpg')
backgrounds.append('largeback/L4.jpg')
backgrounds.append('largeback/L5.jpg')
backgrounds.append('largeback/L6.jpg')
backgrounds.append('largeback/L7.jpg')
backgrounds.append('largeback/L8.jpg')
backgrounds.append('largeback/L9.jpg')


# Load the smaller images
a_image = cv2.imread('images/A.jpg')
b_image = cv2.imread('images/B.jpg')
c_image = cv2.imread('images/C.jpg')
d_image = cv2.imread('images/D.jpg')
e_image = cv2.imread('images/E.jpg')
f_image = cv2.imread('images/F.jpg')
g_image = cv2.imread('images/G.jpg')
h_image = cv2.imread('images/H.jpg')
i_image = cv2.imread('images/I.jpg')
j_image = cv2.imread('images/J.jpg')
k_image = cv2.imread('images/K.jpg')
l_image = cv2.imread('images/L.jpg')
m_image = cv2.imread('images/M.jpg')
n_image = cv2.imread('images/N.jpg')
o_image = cv2.imread('images/O.jpg')
p_image = cv2.imread('images/P.jpg')
q_image = cv2.imread('images/Q.jpg')
r_image = cv2.imread('images/R.jpg')
s_image = cv2.imread('images/S.jpg')
t_image = cv2.imread('images/T.jpg')
u_image = cv2.imread('images/U.jpg')
v_image = cv2.imread('images/V.jpg')
w_image = cv2.imread('images/W.jpg')
x_image = cv2.imread('images/X.jpg')
y_image = cv2.imread('images/Y.jpg')
z_image = cv2.imread('images/Z.jpg')
sp_image = cv2.imread('images/SP.jpg')
qu_image = cv2.imread('images/QU.jpg')
ex_image = cv2.imread('images/EX.jpg')
ap_image = cv2.imread('images/AP.jpg')
da_image = cv2.imread('images/DA.jpg')
am_image = cv2.imread('images/AM.png')
tl_image = cv2.imread('images/TL.jpg')

# Open a file for reading
file = open('puzzles.txt', encoding="utf8")
 
# Read the first line of the file
line = file.readline()

# Loop through the rest of the file and print each line
while line:
    
    objectboundaries = ""
    img = None

    # Pick a random background 
    image = cv2.imread(random.choice(backgrounds))

    # Crop the image to 570x300 - focuses only on the puzzle board area
    x, w, y, h = 75, 570, 120, 305
    crop_img = image[y:y+h, x:x+w]

    # Replace the spaces with underscores
    answer = line.replace(" ", "_")

    # Remove the new line character
    answer = answer.replace("\n", "")

    # Create a unique filename
    unique_string = str(uuid.uuid4())[-10:]

    # Add the letter to the image name - also create a filename for the bounding box data
    image_name = "output/" + unique_string  + ".jpg"
    bound_file = image_name.replace(".jpg", ".xml")
    
    # COnvert sentence into 4 rows that mimic the wheel board
    sentence = line
    rows = split_sentence(sentence)

    # Print the rows
    rownumber = 0
    for row in rows:
        if rownumber == 0 or rownumber == 3: 
            rowsize = 14
        else:
            rowsize = 12

        img = write_row(crop_img, row.strip(), rownumber, 0, rowsize)
        rownumber += 1


    objectboundaries = mystring + objectboundaries + "</annotation>"

    #Write image to file
    bound_file = image_name.replace(".jpg", ".xml")

    objectboundaries = objectboundaries.replace("$filename$", image_name)

    cv2.imwrite(image_name, img)

    fileout = open(bound_file, "w")
    fileout.write(objectboundaries)
    fileout.close()

    line = file.readline()

# Close the file when you're done
file.close()

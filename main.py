import cv2
import mediapipe
import numpy
import autopy

# Initializing cv2 camera
cap = cv2.VideoCapture(0)

# Initializing mediapipe
initHand = mediapipe.solutions.hands
mainHand = initHand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Object to draw the connections between each finger index
draw = mediapipe.solutions.drawing_utils

# Outputs the height and width of the screen (1920 x 1080)
wScr, hScr = autopy.screen.size()

pX, pY = 0, 0  # Previous x and y location
cX, cY = 0, 0  # Current x and y location

wCam, hCam = 640, 480

frameR = 100  # Frame Reduction
smoothening = 7


def handLandmarks(colorImg):
    landmarkList = []  # Default values if no landmarks are tracked

    landmarkPositions = mainHand.process(colorImg)
    landmarkCheck = landmarkPositions.multi_hand_landmarks

    if landmarkCheck:  # Checks if landmarks are tracked
        # Landmarks for each hand
        for hand in landmarkCheck:

            # Loops through the 21 indexes and outputs their landmark coordinates (x, y, z)
            for index, landmark in enumerate(hand.landmark):
                # Draws each individual index on the hand with connections
                draw.draw_landmarks(img, hand, initHand.HAND_CONNECTIONS)
                h, w, c = img.shape
                centerX, centerY = int(landmark.x * w), int(
                    landmark.y * h)  # Converts the decimal coordinates relative to the image for each index
                landmarkList.append([index, centerX, centerY])  # Adding index and its coordinates to a list

    return landmarkList


def fingers(landmarks):
    fingerTips = []  # To store 4 sets of 1s or 0s
    tipIds = [4, 8, 12, 16, 20]  # Indexes for the tips of each finger

    # Check if thumb is up
    if landmarks[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
        fingerTips.append(1)
    else:
        fingerTips.append(0)

    # Check if fingers are up except the thumb
    for id in range(1, 5):
        # Checks to see if the tip of the finger is higher than the joint
        if landmarks[tipIds[id]][2] < landmarks[tipIds[id] - 3][2]:
            fingerTips.append(1)
        else:
            fingerTips.append(0)

    return fingerTips


while True:
    check, img = cap.read()  # Reads frames from the camera
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Changes the format of the frames from BGR to RGB
    lmList = handLandmarks(imgRGB)
    cv2.rectangle(img, (75, 75), (640 - 75, 480 - 75), (255, 0, 255), 2)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]  # Gets index 8s x and y values (skips index value because it starts from 1)
        x2, y2 = lmList[12][1:]  # Gets index 12s x and y values (skips index value because it starts from 1)
        finger = fingers(lmList)  # Calling the fingers function to check which fingers are up

        if finger[1] == 1 and finger[0] == 0:  # Checks to see if the pointing finger is up and thumb finger is down

            # Converts the width of the window relative to the screen width
            x3 = numpy.interp(x1, (frameR, wCam - smoothening), (0, wScr))
            # Converts the height of the window relative to the screen height
            y3 = numpy.interp(y1, (frameR, hCam - smoothening), (0, hScr))

            cX = pX + (x3 - pX) / smoothening  # Stores previous x locations to update current x location
            cY = pY + (y3 - pY) / smoothening  # Stores previous y locations to update current y location

            # Function to move the mouse to the x3 and y3 values (wSrc inverts the direction)
            autopy.mouse.move(wScr - cX, cY)
            pX, pY = cX, cY  # Stores the current x and y location as previous x and y location for next loop

        # Checks to see if the pointer finger is down and thumb finger is up
        if finger[1] == 1 and finger[0] == 1:
            autopy.mouse.click()

            # Check if pointer finger is up and pinky finger is down
        if finger[1] == 1 and finger[4] == 0:
            break

    cv2.imshow("Webcam", img)

    # Other option to stop the program with 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

import cv2
from cvzone.HandTrackingModule import HandDetector

width = 1280
height = 720

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detector = HandDetector(maxHands=1, detectionCon=0.9)

def GetOrient(lmList):
    if lmList[8][0] > lmList[0][0]:
        orient = "right"
    elif lmList[8][0] < lmList[0][0]:
        orient = "left"
    return orient

def PullTrigger(lmList, orient):
    if orient == "right" and lmList[8][0] < lmList [6][0]:
        cv2.putText(img, "Bang!", (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    elif orient == "left" and lmList[8][0] > lmList [6][0]:
        cv2.putText(img, "Bang!", (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return

def GunDetector(lmList):
    orient = GetOrient(lmList)

    aim_x , aim_y = int((lmList[6][0]-lmList[5][0])*3 + lmList[5][0]), int((lmList[6][1]-lmList[5][1])*3 + lmList[5][1])

    # if gun gesture is detected , lmList[8][0] > lmList[7][0]
    if lmList[8][0] > lmList[0][0] and (lmList[12][0] < lmList[10][0] and lmList[16][0] < lmList[14][0]) or\
        lmList[8][0] < lmList[0][0] and (lmList[12][0] > lmList[10][0] and lmList[16][0] > lmList[14][0]):
        cv2.line(img, (lmList[8][0], lmList[8][1]), (lmList[5][0], lmList[5][1]), (255, 0, 0), 2)
        cv2.line(img, (lmList[5][0], lmList[5][1]), (lmList[17][0], lmList[17][1]), (255, 0, 0), 2)
        cv2.line(img, (lmList[17][0], lmList[17][1]), (lmList[18][0], lmList[18][1]), (255, 0, 0), 2)
        cv2.line(img, (lmList[18][0], lmList[18][1]), (lmList[6][0], lmList[6][1]), (255, 0, 0), 2)
        cv2.putText(img, "Gun Detected", (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        cv2.circle(img, (aim_x, aim_y), 20, (0, 255, 0), 2)
        cv2.circle(img, (aim_x, aim_y), 5, (0, 255, 0), -1)

        PullTrigger(lmList, orient)

    return


while True:
    # Get the frame from the webcam
    success, img = cap.read()

    # Hands
    hands, img = detector.findHands(img, draw=False)

    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        #print(lmList)
        GunDetector(lmList)

    # target
    cv2.rectangle(img, (200, 200), (250, 250), (0, 0, 255), -1)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # Break the loop if 'Esc' key is pressed
    if cv2.waitKey(1) & 0xFF == 27:
        break


import cv2
import mediapipe as mp
import time
import math
import numpy as np

class handDetector():
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, minTrackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []

    def findHands(self, img, draw=True, flipType=True):
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.results = self.hands.process(imgRGB)
            allHands = []
            h, w, c = img.shape
            if self.results.multi_hand_landmarks:
                for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                    myHand = {}
                    mylmList = []
                    xList = []
                    yList = []
                    for id, lm in enumerate(handLms.landmark):
                        px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                        mylmList.append([px, py, pz])
                        xList.append(px)
                        yList.append(py)

                    xmin, xmax = min(xList), max(xList)
                    ymin, ymax = min(yList), max(yList)
                    boxW, boxH = xmax - xmin, ymax - ymin
                    bbox = xmin, ymin, boxW, boxH
                    cx, cy = bbox[0] + (bbox[2] // 2), \
                            bbox[1] + (bbox[3] // 2)

                    myHand["lmList"] = mylmList
                    myHand["bbox"] = bbox
                    myHand["center"] = (cx, cy)

                    if flipType:
                        if handType.classification[0].label == "Right":
                            myHand["type"] = "Left"
                        else:
                            myHand["type"] = "Right"
                    else:
                        myHand["type"] = handType.classification[0].label
                    allHands.append(myHand)

                    if draw:
                        self.mpDraw.draw_landmarks(img, handLms,
                                                self.mpHands.HAND_CONNECTIONS)
                        cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                    (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                    (255, 0, 255), 2)
                        cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                                    2, (255, 0, 255), 2)
            if draw:
                return allHands, img
            else:
                return allHands

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin,xmax=min(xList),max(xList)
            ymin,ymax=min(yList),max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
            (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self, myHand):
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]
        if self.results.multi_hand_landmarks:
            fingers = []
            if myHandType == "Right":
                if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            for id in range(1, 5):
                if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img=None):
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            return length, info, img
        else:
            return length, info

    def findDistance(self, p1, p2, img=None):
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            return length, info, img
        else:
            return length, info

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(1)
    detector = handDetector()
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)

        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]
            bbox1 = hand1["bbox"]
            centerPoint1 = hand1['center']
            handType1 = hand1["type"]

            fingers1 = detector.fingersUp(hand1)

            if len(hands) == 2:
                hand2 = hands[1]
                lmList2 = hand2["lmList"]
                bbox2 = hand2["bbox"]
                centerPoint2 = hand2['center']
                handType2 = hand2["type"]

                fingers2 = detector.fingersUp(hand2)

                length, info, img = detector.findDistance(lmList1[8][0:2], lmList2[8][0:2], img)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()
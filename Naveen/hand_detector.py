import numpy as np
import cv2
hand_cascade = cv2.CascadeClassifier(r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\haar_classifiers\hand.xml')

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hands = hand_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x,y,w,h) in hands:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    cv2.imshow('frame',frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()

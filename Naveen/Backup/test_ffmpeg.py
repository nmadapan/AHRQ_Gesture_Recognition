import numpy as np
import cv2

filepath = "D:\\AHRQ\\Study_IV\\Data\\L2\\1_1_S2_L2_Scroll_Up_rgb.avi"
writepath = "C:\\Users\\raman\\Desktop\\output.avi"

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(writepath,fourcc, 20.0, (1920,1080))

cap = cv2.VideoCapture(filepath)

while(cap.isOpened()):
    ret, frame = cap.read()
    out.write(frame)
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
import cv2 as cv

print cv.__version__

cap = cv.VideoCapture('./sample_video.mp4')
while cap.isOpened():
	ret, frame = cap.read()
	cv.imshow('Image', cv.resize(frame, None, fx=0.5, fy=0.5))
	if cv.waitKey(1) == ord('q'): break

cap.release()
cv.destroyAllWindows()
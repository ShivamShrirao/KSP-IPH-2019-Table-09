import cv2
import os
import pickle
import face_recognition
from time import sleep

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


def train(name,imagePaths):
	knownEncodings=[]
	knownNames=[]
	for imagePath in imagePaths:
		img = cv2.imread(imagePath)
		rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

		boxes = face_recognition.face_locations(rgb,model='hog')
		encodings = face_recognition.face_encodings(rgb,boxes)

		for encoding in encodings:
			knownEncodings.append(encoding)
			knownNames.append(name)

	data = {"encodings":knownEncodings,"names":knownNames}
	return data


def recognize(imagePaths,data):
	names = []
	if type(imagePaths)==str:
		imagePaths=[imagePaths]
	show_FLAG=False
	for imagePath in imagePaths:
		img=cv2.imread(imagePath)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)

		boxes = [(y,x+w,y+h,x) for (x,y,w,h) in faces]
		encodings = face_recognition.face_encodings(rgb,boxes)

		for encoding in encodings:
			matches = face_recognition.compare_faces(data["encodings"],encoding)
			name="Unknown"
			if True in matches:
				show_FLAG=True
				matchIdx = [i for (i,b) in enumerate(matches) if b]
				counts = {}

				for i in matchIdx:
					name=data["names"][i]
					counts[name] = counts.get(name,0) + 1

				name = max(counts,key=counts.get)
			names.append(name)
		if show_FLAG:
			for((top,right,bottom,left),name) in zip(boxes,names):
				cv2.rectangle(img,(left,top),(right,bottom),(0,0,255),2)
				y = top-15 if top-15>15 else top+15
				cv2.putText(img,name,(left,y),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,0,255),2)
			cv2.imshow('webcam', img)
			while 1:
				key = cv2.waitKey(1) & 0xff
				if key == ord('q'):
					cv2.destroyAllWindows()
					break
	print(names)
	return names

# enc=train("SID",["sid.jpg"])

# imagePath="Screenshot.png"
# recognize(imgPath,enc)

TARGET="TARGET"
def count_targets(trainImgs,recImgs):		# (list,list) give it lists
	enc=train(name=TARGET,imagePaths=trainImgs)
	mIdx=0
	mx=0
	for idx,rmg in enumerate(recImgs):
		nms=recognize(imagePaths=rmg,data=enc)
		nc=nms.count(TARGET)
		if nc>mx:
			mx=nc
			mIdx=idx
	return mIdx
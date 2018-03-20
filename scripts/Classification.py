# -*- coding: utf-8 -*-

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
import IO
import numpy as np
import cv2
#import pickle
import numpy as np
import Detection as detect

# default path
datapath = "/src/data/"

# ~~ CLASSIFIERS ~~
lda = LDA()
svm = svm.SVC(kernel='linear')
knn = KNeighborsClassifier()
gaussian = GaussianProcessClassifier(1.0 * RBF(1.0))


# Classification by area
# objects: list of borders coordinates
# raidius: central circle radius
# bimage: binary image
def area_lenght_classification(objects, radius, bimage):
	eggs = []
	clusters = []

	for i in range(len(objects)):
		area = len(detect.get_object_area(objects[i], bimage)) / radius
		
		if area > 0.1 and area < 0.32:
			eggs.append(objects[i])

		elif area >= 0.32:
			clusters.append(objects[i])

	print("Lenght analysis: " + str(len(eggs)) + " eggs.")
	print("Lenght analysis: " + str(len(clusters)) + " clusters.")

	return eggs, clusters



# Classification of shapes!
# shape: Feret measures
# eggs: list of eggs objects
def border_shape_classification(shapes, eggs, filename):
	knowledge = IO.open_data(datapath +	str(filename))

	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	gaussian.fit(x_train, y_train)

	reggs = []

	for i in range(len(shapes)):
		predict = gaussian.predict(np.array(shapes[i]).reshape(1, -1))[0]

		if predict == 0:
			reggs.append(eggs[i])

	print("Shape analysis: " + str(len(reggs)) + ".")

	return reggs



# Classification of objects according to its color
# colors: array of colors
# eggs: list containing eggs objects
# clusters: lits containing cluster objects
def object_color_classification(colors, objects, isEgg):
	knowledge = None

	if isEgg == True:
		knowledge = IO.open_data(datapath +	"cl.dat")
	else:
		knowledge = IO.open_data(datapath +	"clcls.dat")


	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	gaussian.fit(x_train, y_train)

	robjects = []

	if colors != None:
		for i in range(len(colors)):
			predict = gaussian.predict(np.array(colors[i]).reshape(1, -1))[0]

			#print predict
			if predict == 0:
				robjects.append(objects[i])

	return robjects



# Image segmentation based on pixel level color classification.
# imrgb: RGB image
def color_segmentation(imrgb):
	width, height = imrgb.shape[:2]

	imhsv = cv2.cvtColor(imrgb, cv2.COLOR_BGR2HSV)
	imlab = cv2.cvtColor(imrgb, cv2.COLOR_BGR2LAB)

	r = imrgb[:,:,2].reshape(1, -1) / 255
	g = imrgb[:,:,1].reshape(1, -1) / 255
	b = imrgb[:,:,0].reshape(1, -1) / 255
	rg = (r - g) / 255
	rb = (r - b) / 255
	gr = (g - r) / 255
	gb = (g - b) / 255
	br = (b - r) / 255
	bg = (b - g) / 255
	g2rb = (2 * g - r - b) / 255
	h = imhsv[:,:,0].reshape(1, -1) / 255
	s = imhsv[:,:,1].reshape(1, -1) / 255
	v = imhsv[:,:,2].reshape(1, -1) / 255
	l = imlab[:,:,0].reshape(1, -1) / 255
	a = imlab[:,:,1].reshape(1, -1) / 255
	b = imlab[:,:,2].reshape(1, -1) / 255

	colormat = np.concatenate((r,g,b,rg,rb,gr,gb,br,bg,g2rb,h,s,v,l,a,b), axis=0)
	colormat = colormat.transpose()

	'''
	data = IO.open_data(datapath +	str('clseg.dat'))
	datx = data[:, :-1]
	daty = data[:, -1:]

	#clf = GaussianProcessClassifier()
	svm.fit(datx, daty)
	'''

	svm = pickle.load(open(datapath + 'clseg.sav', 'rb'))

	res = svm.predict(colormat)
	res = res.reshape(width, height)

	return res
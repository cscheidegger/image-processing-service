# -*- coding: utf-8 -*-

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
import IO
import numpy as np
import cv2
import pickle
import numpy as np
import Detection as detect

# default path
datapath = IO.get_root(__file__) + "/../data/"

# ~~ CLASSIFIERS ~~
lda = LDA()
svm = svm.SVC(kernel='linear')
knn = KNeighborsClassifier()
gaussian = GaussianProcessClassifier(1.0 * RBF(1.0))


# Classification by area
# objects: list of borders coordinates
# raidius: central circle radius
# bimage: binary image
def classification_by_area_lenght(objects, radius, threshold):
	eggs = []
	clusters = []

	thres_min, thres_max = threshold

	for obj in objects:
		nlenght = len(obj) / radius
		
		if nlenght > thres_min and nlenght < thres_max:
			eggs.append(obj)

		elif nlenght >= thres_max:
			clusters.append(obj)

	return eggs, clusters



# Classification of shapes!
# shape: Feret measures
# eggs: list of eggs objects
def classification_by_border_shape(shapes, eggs, filename):
	knowledge = IO.open_data(datapath +	str(filename))

	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	gaussian.fit(x_train, y_train)

	reggs = []

	for i in range(len(shapes)):
		predict = gaussian.predict(np.array(shapes[i]).reshape(1, -1))[0]

		if predict == 0:
			reggs.append(eggs[i])

	return reggs



# Classification of objects according to its color
# colors: array of colors
# eggs: list containing eggs objects
# clusters: lits containing cluster objects
def classification_by_area_color(colors, objects, isEgg):
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

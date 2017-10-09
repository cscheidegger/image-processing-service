# -*- coding: utf-8 -*-

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Clasification.py														  #
# Author: João Herrera		Date: 18 ago, 2017							  #
#																		  #
# These methods are used to perform some classification algorithms like   #
# LDA or any other...													  #
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
import IO
import numpy as np


# default path
datapath = "data/"

# ~~ CLASSIFIERS ~~
lda = LDA()
svm = svm.SVC(kernel='linear')
knn = KNeighborsClassifier()

# Classificate borders according to its lenght
# objects: list of borders coordinates
def border_lenght_classification(objects, radius):
	eggs = []
	clusters = []

	for i in range(len(objects)):
		ratio = objects[i]['lenght'] / radius

		if ratio > 0.19 and ratio < 0.31:
			eggs.append(objects[i])

		elif ratio >= 0.31 and ratio < 0.80:
			clusters.append(objects[i])

	return eggs, clusters



# Classification of shapes!
# shape: Feret measures
# eggs: list of eggs objects
def border_shape_classification(shapes, eggs, filename):
	knowledge = IO.open_data(datapath +	str(filename))

	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	svm.fit(x_train, y_train)

	reggs = []

	for i in range(len(shapes)):
		predict = svm.predict(np.array(shapes[i]).reshape(1, -1))[0]

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

	lda.fit(x_train, y_train)

	robjects = []

	if colors != None:
		for i in range(len(colors)):
			predict = lda.predict(np.array(colors[i]).reshape(1, -1))[0]

			#print predict
			if predict == 0:
				robjects.append(objects[i])

	return robjects



# Classification of clusters according to its texture
# textures: array with textures histograms
# clusters: array containing cluster objects
def cluster_texture_classification(textures, clusters):
	knowledge = IO.open_data(datapath +	"tx.dat")

	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	lda.fit(x_train, y_train)

	rclusters = []

	for i in range(len(clusters)):
		predict = lda.predict(np.array(textures[i]).reshape(1, -1))[0]

		print(predict)
		
		if predict == 0:
			rclusters.append(clusters[i])

	return rclusters
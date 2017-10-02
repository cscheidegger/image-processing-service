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
import IO
import numpy as np


# default path
datapath = "data/"

# ~~ CLASSIFIERS ~~
clf = LDA()
#clf = svm.SVC()

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

	'''
	knowledge = IO.open_data(datapath +	"sz.dat")

	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	# fit training
	clf.fit(x_train, y_train)

	eggs = []
	clusters = []

	# start classification
	for i in range(len(objects)):
		predict = clf.predict(np.array([objects[i]['lenght'] / radius, objects[i]['lenght']]).reshape(1, -1))[0]

		# if the object isn't an egg or a cluster of eggs... remove it!
		if predict == 1:
			eggs.append(objects[i])

		elif predict == 2:
			clusters.append(objects[i])

	print "Borders size: " + str(len(eggs)) + " eggs."
	print "Borders size: " + str(len(clusters)) + " clusters."

	return eggs, clusters
	'''

# Classification of shapes!
# shape: Feret measures
# eggs: list of eggs objects
def border_shape_classification(shapes, eggs, filename):
	knowledge = IO.open_data(datapath +	str(filename))

	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	clf.fit(x_train, y_train)

	reggs = []

	for i in range(len(shapes)):
		predict = clf.predict(np.array(shapes[i]).reshape(1, -1))[0]

		if predict == 0:
			reggs.append(eggs[i])

	print "Shape analysis: " + str(len(reggs)) + "."

	return reggs


# Classification of objects according to its color
# colors: array of colors
# eggs: list containing eggs objects
# clusters: lits containing cluster objects
def object_color_classification(colors, objects):
	knowledge = IO.open_data(datapath +	"cl.dat")

	x_train = knowledge[:, :-1]
	y_train = knowledge[:, -1:]

	clf.fit(x_train, y_train)

	robjects = []

	for i in range(len(colors)):
		predict = clf.predict(np.array(colors[i]).reshape(1, -1))[0]

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

	clf.fit(x_train, y_train)

	rclusters = []

	for i in range(len(clusters)):
		predict = clf.predict(np.array(textures[i]).reshape(1, -1))[0]
		print predict
		if predict == 0:
			rclusters.append(clusters[i])

	return rclusters
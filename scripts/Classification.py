# -*- coding: utf-8 -*-

import IO
import numpy as np
import pickle

# default path
datapath = IO.get_root(__file__) + "/../data/"


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



# Classification of objects according to the .ipk file
# features: array of features
# objects: array of objects
# filename: .ipk file path
def classification_by_ipk(features, objects, filename):

	if len(features) == 0:
		return []

	classifier = pickle.load(open(datapath + filename, 'rb'))

	predicts = classifier.predict(np.array(features)).flatten().astype(int)
	robjects = np.array(objects)[predicts == 0]

	return robjects
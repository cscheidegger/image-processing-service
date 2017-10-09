# -*- coding: utf-8 -*-

import cv2
import numpy as np

from skimage import io, feature, img_as_ubyte, morphology, transform, measure, draw, exposure, color
from scipy.spatial import distance
from scipy.ndimage.morphology import binary_fill_holes
from sklearn.cluster import KMeans

# Detect the central circle. This is useful to correctly crop the palette image
# image: rgb image
def detect_circle_mark(image):

	# first step: segmenting the central circle using Canny
	gsimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# local histogram equalization
	clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(2,2))
	gsimage = clahe.apply(gsimage)

	bimage = feature.canny(gsimage, sigma=3)
	bimage = img_as_ubyte(bimage) # converting image format to unsigned byte


	# dilating the circle. It makes easy the identification performed by ransac algorithm.
	#bimage = morphology.dilation(bimage, morphology.disk(6))
	coords = np.column_stack(np.nonzero(bimage))

	# detecting circle using ransac.
	if len(coords) > 0:
		model, inliers = measure.ransac(coords, measure.CircleModel, min_samples=3, residual_threshold=1, max_trials=1000)	
	
	else:
		return None

	# checking if the radius has an acceptable value
	gsrows, gscols = gsimage.shape

	for param in model.params:
		if param < 0: #or (param > gsrows or param > gscols):
			return None


	rr, cc = draw.circle_perimeter(int(model.params[0]), int(model.params[1]), int(model.params[2]), shape=image.shape)
	gsimage[rr, cc] = 0

	#io.imsave("/home/joaoherrera/Desktop/outw.jpg", gsimage)

	return model.params # center X, center Y, radius




# Detect the contour of all objects in the image
# bimage: binary image
def object_detection(bimage):

	x, y = np.where(bimage == 255)
	coord = np.c_[x, y]

	objects = []
	processed_obj = []
	to_be_processed_obj = []

	while len(coord) > 0:

		if len(to_be_processed_obj) == 0:
			to_be_processed_obj.append(coord[0].tolist())

			if len(processed_obj) > 0:
				objects.append({'pixels': np.array(processed_obj), 'lenght': len(processed_obj)})
				processed_obj = []


		pixel = to_be_processed_obj.pop(0)

		# remove central pixel
		coord = np.delete(coord, np.where(np.logical_and(coord[:, 0] == pixel[0], coord[:, 1] == pixel[1])), 0)


		# finding neighbors with value equals 255
		rows = np.logical_or(coord[:, 0] == pixel[0] - 1, coord[:, 0] == pixel[0] + 1)
		rows = np.logical_or(rows, coord[:, 0] == pixel[0])

		cols = np.logical_or(coord[:, 1] == pixel[1] - 1, coord[:, 1] == pixel[1] + 1)
		cols = np.logical_or(cols, coord[:, 1] == pixel[1])

		items = np.logical_and(rows, cols)
		index = np.where(items)
		items = coord[items]

		# removing neighbors from the global pixels list
		coord = np.delete(coord, index, 0)
		
		# add and create a dictionary according
		if len(items) > 0:
			for item in items:
				to_be_processed_obj.append(item.tolist())


		processed_obj.append(pixel)


	if len(processed_obj) > 0:
		objects.append({'pixels': np.array(processed_obj), 'lenght': len(processed_obj)})


	return objects



# Created for get the best option of pixel which pass across the points of line equation.
def _second_point_line_eq(ref, points):
	candidates = []
	maxdist = 1
	near_id = 1
	p2 = 0

	mxid = 0
	for pixel in points:
		pid = pixel[0]

		if pid > mxid:
			mxid = pid


	while maxdist == 1 and near_id <= mxid:		

		for pixel in points:
			if pixel[0] == points[near_id][0]:
				candidates.append(pixel[1])

		for pixel in candidates:
			dist = distance.euclidean(ref, pixel) 

			if dist > maxdist:
				maxdist = dist
				p2 = pixel

		near_id +=1

	return p2


# Detects shape features of an object over an image
# object: coordinates of an object.
def shape_detection(egg):

	pixels = egg['pixels']

	# find the maximum distance between two points.
	distmat = distance.squareform(distance.pdist(pixels, 'euclidean'))
	mxdist = np.max(distmat)
	dist_id = np.argwhere(distmat == mxdist)[0]

	pa = dist_id[0]
	pb = dist_id[1]
	

	# find the equation of major axis (which fits the 2 known points).
	# next, compute the perpendicular line and get both left and right points.
	x0 = pixels[pa][0]
	y0 = pixels[pa][1]
	y = pixels[pb][1]
	x = pixels[pb][0]

	coef1 = float(y - y0)
	coef2 = float(x - x0)

	p1 = 0
	p2 = 0
	dist = 0

	if coef1 != 0 and coef2 != 0:

		# slope (coeficient a)
		a = float(y - y0) / float(x - x0)

		# -------- perpendicular line
		# the perpendicular line must cross the center of original line
		minor_y = y if y < y0 else y0
		minor_x = x if x < x0 else x0

		y0 = np.round(abs(y - y0) / 2) + minor_y
		x0 = np.round(abs(x - x0) / 2) + minor_x

		a = -1/a # a perpendicular line has the oposite value of slope of the original line

		# fundamental equation of line
		# finding coeficient b
		# y - y0 = m * (x - x0) -> y = ax + b
		b = a * -x0 + y0

		# find the 2 points which cancell the equation 
		points = []
		feasible = []

		for pix in pixels:
			points.append([np.abs(pix[1] - np.round(a * pix[0] + b)), pix])

			if pix[1] == np.round(a * pix[0] + b):
				feasible.append(pix)


		# if we don't get atleast 2 points, let's get the closest one
		if len(feasible) < 2:
			points = sorted(points, key=lambda diff: diff[0])

			if len(feasible) == 0:
				p1 = points[0][1]
				p2 = _second_point_line_eq(p1, points)

			elif len(feasible) == 1:
				p1 = feasible[0]
				p2 = _second_point_line_eq(p1, points)

			dist = distance.euclidean(p1, p2)

		elif len(feasible) == 2:
			p1 = feasible[0]
			p2 = feasible[1]

			dist = distance.euclidean(p1, p2)

		else: # get the pixels which has the farthest distance
			for i in range(len(feasible)):
				for j in range(len(feasible)):
					d = distance.euclidean(feasible[i], feasible[j])

					if d > dist:
						dist = d
						p1 = feasible[i]
						p2 = feasible[j]

	else:
		minor_y = y if y < y0 else y0
		minor_x = x if x < x0 else x0

		cy = np.round(abs(y - y0) / 2) + minor_y
		cx = np.round(abs(x - x0) / 2) + minor_x

		candidates = []

		# coluna 0
		if coef1 == 0:
			candidates = pixels[pixels[:, 0] == cx]

		# linha 0
		else:
			candidates = pixels[pixels[:, 1] == cy]

		dist = 0
		for i in range(len(candidates)):
			for j in range(len(candidates)):
				d = distance.euclidean(candidates[i], candidates[j])

				if d > dist:
					dist = d
					p1 = candidates[i]
					p2 = candidates[j]


	return [mxdist, dist]
	


# Return the pixels inside a set of border coordinates
# object: coordinates set of an object
def get_object_area(object, bimage):

	bdpixels = object['pixels']

	# draw eggs/clusters on a copy of bimage
	bcknim = np.zeros_like(bimage)
	bcknim[bdpixels[:, 0], bdpixels[:, 1]] = 255

	# Get the area of the object
	#bimage = morphology.binary_dilation(bimage)
	bcknim = binary_fill_holes(bcknim)
	bcknim = morphology.binary_erosion(bcknim)
	bcknim = img_as_ubyte(bcknim) # converting image format to unsigned byte
	
	arpixels = np.argwhere(bcknim == 255)

	return arpixels



# Return the true colors info of an object
# Format: EggRGB + BackgroundRGB + Luminance(eggs) -
def get_object_color(obcoord, imRGB, imHSV, imLAB):

	cfeat = [] # Color features

	if len(obcoord) == 0:
		return None

	background_BGR_mean = np.mean(imRGB, axis=(1, 0)) 	# mean of whole picture
	background_HSV_mean = np.mean(imHSV, axis=(1, 0))
	background_LAB_mean = np.mean(imLAB, axis=(1, 0))

	for id_ob in range(len(obcoord)):
		colors = []
		colors.append(np.abs(np.mean(imRGB[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0) - background_BGR_mean))
		colors.append(np.abs(np.mean(imHSV[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0) - background_HSV_mean))
		colors.append(np.abs(np.mean(imLAB[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0) - background_LAB_mean))

		cfeat.append(np.array(colors).flatten())

	return cfeat
	


# Get the cluster texture using LBPriu2
# cluster: area of a cluster
# imGray: gray-scale image
def get_cluster_texture(cluster, imGray):

	imLBP = feature.local_binary_pattern(imGray, 8, 1, 'uniform')
	pixels = imLBP[cluster[:, 0], cluster[:, 1]]

	histLBP = np.histogram(pixels, bins=9)[0]

	return histLBP
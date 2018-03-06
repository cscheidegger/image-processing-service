# -*- coding: utf-8 -*-

import cv2
import numpy as np

from skimage import io, feature, img_as_ubyte, morphology, transform, measure, draw, exposure, color, segmentation
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
		if param < 0 or (param > gsrows or param > gscols):
			return None


	rr, cc = draw.circle_perimeter(int(model.params[0]), int(model.params[1]), int(model.params[2]), shape=image.shape)
	gsimage[rr, cc] = 0


	return model.params # center X, center Y, radius



# There are cases that a cluster might be on the circle pixels.
# To get only the ROI of these clusters, we need to reduce the contrast between the circle pixels and the background
# image: RGB image
# params: center coordinates and radius of circle
def remove_central_circle(image, params):
	gsimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# creating mask...
	# in this mask we gonna draw the central circle, dilate it and replace its pixels by neighbors values of original sample.
	mask = np.zeros_like(gsimage)

	cv2.circle(mask, (int(params[1]), int(params[0])), int(params[2]), (255, 255, 255))
	mask = morphology.binary_dilation(mask, selem=morphology.selem.disk(18))

	# get pixels
	coords = np.c_[np.where(mask > 0)]

	# apply a filter to remove/reduce the contrast between circle and background
	ksize = 21 # kernel size


	# get all the pixels of the circle and compute the mean value of its neighbors
	for pair in coords:
		x = pair[0]
		y = pair[1]

		meanpx = gsimage[x - ksize // 2 : x + ksize // 2, y - ksize // 2 : y + ksize // 2]
		meanpx = meanpx[meanpx > gsimage[x, y]] #meanpx = meanpx[(meanpx[:,:,0] > image[x, y, 0]) & (meanpx[:,:,1] > image[x, y, 1]) & (meanpx[:,:,2] > image[x, y, 2])]
		cntrpx = len(meanpx)
		meanpx = np.sum(meanpx)
		meanpx = meanpx // (cntrpx + 1)
		image[x, y] = (meanpx, meanpx, meanpx)


	return image



# This method reduces the contrast between the lines located at the border of the palette and the background
# image: RGB image
def remove_border_lines(image):

	# converting image to grayscale
	gsimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# canny segmentation
	cyimage = feature.canny(gsimage, sigma=3)
	cyimage = morphology.binary_dilation(cyimage, selem=morphology.disk(3))
	cyimage = img_as_ubyte(cyimage) # converting image format to unsigned byte

	# computing hough lines...
	hlines = cv2.HoughLinesP(cyimage, 1, np.pi/500, 50, 100, 100)
	
	if type(hlines) == type(None):
		return image

	lines = []
	binary = np.zeros_like(gsimage)

	for line in hlines:
		line = line[0]
		cv2.line(binary, (line[0], line[1]), (line[2], line[3]), (255,255,255), 3)


	binary = morphology.binary_dilation(binary, selem=morphology.selem.disk(18))
	rows, cols = binary.shape[:2]

	# getting coordinates of nonzero values
	coords = np.column_stack(np.nonzero(binary))

	ksize = 27 # kernel size
	for pair in coords:
		x = pair[0]
		y = pair[1]

		meanpx = 0
		cntrpx = 1
		value = gsimage[x, y]

		xx = ksize // 2
		yy = ksize // 2

		if (x + xx) > rows - 1:
			xx = rows - 1

		elif (x - xx) < 0:
			xx = 0

		if (y + yy) > cols - 1:
			yy = cols - 1

		elif (y - yy) < 0:
			yy = 0


		meanpx = gsimage[x - xx : x + xx, y - yy : y + yy]
		meanpx = meanpx[meanpx > gsimage[x, y]] 
		cntrpx = len(meanpx)
		meanpx = np.sum(meanpx)
		meanpx = meanpx // (cntrpx + 1)
		image[x, y] = (meanpx, meanpx, meanpx)

	return image



# Detect the contour of all objects in the image
# bimage: binary image
def object_detection(bimage):
	imseg = img_as_ubyte(segmentation.find_boundaries(bimage, connectivity=1, mode='outer', background=1)) # segmented image
	x, y = np.where(imseg == 255)
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



# Created to get the best option of pixel which pass across the points of line equation.
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


	
# Giving a try to close gaps in the border of clusters
# bimage: binary image
def closing_gaps(bimage):

	# dilation followed by erosion 7x
	kernel = np.ones((3,3),np.uint8)
	dilation = cv2.dilate(bimage, kernel, iterations = 10)
	bimage = cv2.erode(dilation, kernel, iterations = 10)

	# closing all object
	bimage = binary_fill_holes(bimage)

    # get the contour
	cimage = np.zeros_like(bimage)
	im, contours, hierarchy = cv2.findContours(img_as_ubyte(bimage), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

	for contour in contours:
		contour = contour.reshape((contour.shape[0], contour.shape[2]))
		cimage[contour[:, 1], contour[:, 0]] = 255

	cimage = morphology.binary_dilation(cimage)

	return img_as_ubyte(cimage)



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
# Format: 
# red + 
# green + 
# blue + 
# red - green + 
# red - blue +
# green - red +
# green - blue +
# blue - red +
# blue - green +
# 2 x green - red - blue +
# hue +
# saturation +
# value +
# luminance +
# a +
# b
def get_object_color(obcoord, imrgb, imhsv, imlab):

	cfeat = [] # Color features

	if len(obcoord) == 0:
		return None

	r = imrgb[:,:,2] / 255
	g = imrgb[:,:,1] / 255
	b = imrgb[:,:,0] / 255
	rg = (r - g) / 255
	rb = (r - b) / 255
	gr = (g - r) / 255
	gb = (g - b) / 255
	br = (b - r) / 255
	bg = (b - g) / 255
	g2rb = (2 * g - r - b) / 255
	h = imhsv[:,:,0] / 255
	s = imhsv[:,:,1] / 255
	v = imhsv[:,:,2] / 255
	l = imlab[:,:,0] / 255
	a = imlab[:,:,1] / 255
	b = imlab[:,:,2] / 255


	for id_ob in range(len(obcoord)):
		colors = []

		colors.append(np.abs(np.mean(r[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(g[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(b[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(rg[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(rb[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(gr[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(gb[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(br[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(bg[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(g2rb[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(h[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(s[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(v[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(l[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(a[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))
		colors.append(np.abs(np.mean(b[obcoord[id_ob][:, 0], obcoord[id_ob][:, 1]], axis=0)))

		cfeat.append(np.array(colors).flatten())
		
	return cfeat

# -*- coding: utf-8 -*-

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Defects.py														  	  #
# Author: João Herrera		Date: 25 ago, 2017							  #
#																		  #
# These methods are used to detect some defects in the input image		  #
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import numpy as np
import cv2
import IO
import Detection
import DeepLearning
import Classification

from scipy.ndimage.filters import gaussian_filter1d

# return the blurry rate of a given image
# im: RGB image
def isBlurred(im):
	blur = cv2.Laplacian(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()

	print("Blur rate: " + str(blur))

	return blur


# check if the image is too dark.
# im: RGB image
def isDark(im):
	histogram = np.histogram(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).ravel(), 256, [0, 256])[0]
	bright_rate = np.argwhere(histogram == np.max(histogram))[0][0]

	print("Brightness rate: " + str(bright_rate))

	return bright_rate



# check if the image has large shadows that can hinder the egg recognition process.
# gscroped: RGB image
def shadow_index(im):
	luminance = cv2.cvtColor(im, cv2.COLOR_BGR2Lab)[:, :, 0]
	histogram = np.histogram(luminance.ravel(), bins=2)[0]
	shadow_rate = float(histogram[0]) / float(histogram[1])

	print("Shadow rate: " + str(shadow_rate))

	return shadow_rate



# This method uses deep learning techniques to recognize if the input image has or not a palette.
# To be a valid palette, neural network must find both palette shape and central circle.
# The retured value is the palette dimension.
# im: RGB image
def hasPalette(im):
	coordinates, probs = DeepLearning.get_features(im)

	if len(probs) > 0:
		print(probs)
		# sort values from the highest to lowest

		palettes = np.argwhere(probs[:, 0] == "palette")
		if len(palettes) > 0:
			palettes = palettes[0]
			palettes = probs[palettes]
			palettes = sorted(palettes, key=lambda palette: palette[1], reverse=True)[0]

		circles = np.argwhere(probs[:, 0] == "circle")
		if len(circles) > 0:
			circles = circles[0]
			circles = probs[circles]
			circles = sorted(circles, key=lambda circle: circle[1], reverse=True)[0]

		# check if there's atleat one palette and one probs
		if len(palettes) > 0 and len(circles) > 0:
			
			# The objects are validated if and only if its recognition score are higher than 98%
			if float(palettes[1]) <= 0.98:
				print(IO.json_packing_error('ERR_005'))
				return 'error'
			
			if float(circles[1]) <= 0.98:
				print(IO.json_packing_error('ERR_003'))
				return 'error'

			coord = coordinates[np.where(probs[:, 1] == palettes[1])[0][0]]
			im = im[coord[1] : coord[3], coord[0] : coord[2]] # crop image

			#cv2.imwrite('/home/joaoherrera/Desktop/out.jpg',im)	
			return im

		elif len(palettes) == 0 and len(circles) == 0:
			print(IO.json_packing_error('ERR_006'))
			return 'error'


		elif len(palettes) > 0:
			print(IO.json_packing_error('ERR_003'))
			return 'error'

		else:
			print(IO.json_packing_error('ERR_005'))
			return 'error'

	else:
		print(IO.json_packing_error('ERR_006'))
		return 'error'



# Glare recognition algorithm. The best solution found is to recognize it by texture analysis.
# imRGB: RGB image
def watermark_detection(imRGB):
	luminance = cv2.cvtColor(imRGB, cv2.COLOR_BGR2Lab)[:, :, 0]


	# histogram analysis must be done locally
	framesize = 200
	rows, cols = luminance.shape

	#..then we crop the whole image into squares of framesize x framesize
	areas = []
	for row in range((rows - 1) // framesize):
		for col in range((cols - 1) // framesize):
			areas.append(luminance[row * framesize : (row + 1) * framesize, col * framesize : (col + 1) * framesize])


	# check all areas..
	for area in areas:
		histogram = []

		# extract its histogram
		for i in range(256):
			histogram.append(len(area[area == i]))

		# find the bin which has more pixels
		mean = np.where(histogram == np.max(histogram))[0][0] 

		histogram = histogram[mean:] 
		histogram = gaussian_filter1d(histogram, sigma=2) # gaussian filter to smooth the histogram

		minimum = np.min(histogram)
		minpos = np.where(histogram == np.min(histogram))[0][0]

		if minpos < (len(histogram) - 5):

			if np.sum(histogram[-5:]) > 50:
				return True

	return False

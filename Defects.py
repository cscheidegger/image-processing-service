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

from scipy.signal import argrelextrema

import DeepLearning

from scipy import signal
from skimage import io, filters


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
				return error
			
			if float(circles[1]) <= 0.98:
				print(IO.json_packing_error('ERR_003'))
				return error

			coord = coordinates[np.where(probs[:, 1] == palettes[1])[0][0]]
			im = im[coord[1] : coord[3], coord[0] : coord[2]] # crop image

			#cv2.imwrite('/home/joaoherrera/Desktop/out.jpg',im)	
			return im

		elif len(palettes) == 0 and len(circles) == 0:
			print(IO.json_packing_error('ERR_006'))
			return error


		elif len(palettes) > 0:
			print(IO.json_packing_error('ERR_003'))
			return error

		else:
			print(IO.json_packing_error('ERR_005'))
			return error

	else:
		print(IO.json_packing_error('ERR_006'))
		return error





# -*- coding: utf-8 -*-

import numpy as np
import cv2
import IO
import Detection
import DeepLearning
import Classification

from scipy.ndimage.filters import gaussian_filter1d
from skimage import feature

# return the blurry rate of a given image
# im: RGB image
def isBlurred(im):
	rows, cols = im.shape[:2]
	cbimage = feature.canny(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), sigma=3)
	nonzero = np.count_nonzero(cbimage)
	blur = nonzero * 1000 / (rows * cols)

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

	if not check_background(im, coordinates[0]):
		print(IO.json_packing_error('ERR_011'))
		return 'error'

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

		if len(circles) > 0 and len(palettes) > 0:

			# validation by score
			# The objects are validated if and only if its recognition score are higher than 98%
			if np.round(float(palettes[1])) <= 0.98 or np.round(float(circles[1])) <= 0.97:
				print(IO.json_packing_error('ERR_009'))
				return 'error'
				

			# validation by position
			# The objective is to check the position of the central circle.
			# Once it is not centered the validation is rejected
			height, width = im.shape[:2]

			coordC = coordinates[1]
			coordCx1 = coordC[0]
			coordCy1 = coordC[1]
			coordCx2 = coordC[2]
			coordCy2 = coordC[3]

			disttop = coordCy1
			distleft = coordCx1
			distright = width - coordCx2
			distdown = height - coordCy2

			horck = np.abs(distleft - distright)
			verck = np.abs(disttop - distdown)

			if horck > np.min([distleft, distright]) or verck > np.min([disttop, distdown]) / 1.25:
				print(IO.json_packing_error('ERR_010'))
				return 'error'

			return im
			
		else:
			print(IO.json_packing_error('ERR_009'))
			return 'error'

	else:
		print(IO.json_packing_error('ERR_009'))
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

		minpos = np.where(histogram == np.min(histogram))[0][0]

		if minpos < (len(histogram) - 5):

			if np.sum(histogram[-5:]) > 50:
				return True

	return False



# Check if background is white or something close to it
# imrgb: RGB image
# card_coord: pallete coordinates
def check_background(imrgb, card_coord):
	imgray = cv2.cvtColor(imrgb, cv2.COLOR_BGR2LAB)[:,:,0]

	bckgndL = np.array(imgray[:card_coord[1], :]).flatten()
	bckgndT = np.array(imgray[:, :card_coord[0]]).flatten()
	bckgndR = np.array(imgray[:, card_coord[2]:]).flatten()
	bckgndB = np.array(imgray[card_coord[3]:, :]).flatten()

	bckgnd = np.concatenate((bckgndL, bckgndT, bckgndR, bckgndB)).mean()

	print("Background brightness: " + str(bckgnd))

	if bckgnd < 100:
		return False

	return True
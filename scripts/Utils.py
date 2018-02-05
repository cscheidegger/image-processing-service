# -*- coding: utf-8 -*-

import numpy as np
import cv2
import IO
from scipy import ndimage


# Crop image acording to the center and radius of the palette
# image: rgb image
# circle_params: circle params
def crop_image(image, circle_params):
	rows, cols = image.shape[:2]

	center_x = circle_params[0]
	center_y = circle_params[1]
	radius = circle_params[2]

	c = 1.5 # constant determining how long is the superior/inferior area to be croped.
	b = ((radius * 54) / 12) / 2 # left/right border factor

	if cols > rows:
		image = ndimage.rotate(image, 90)
		center_x, center_y = center_y, center_x
		rows, cols = cols, rows


	x = int(center_x - c * radius)
	y = int(center_y - b)
	width = int(2 * c * radius)
	height = int(2 * b)


	if x < 0:
		x = 0

	if y < 0:
		y = 0

	if width > cols:
		width = cols - 1

	if height > rows:
		height = rows - 1

	#print x, y, width, height
	roi = image[x : x + width, y : y + height]

	return roi


 
# During a few tests, some of the circles weren't been correctfully identified.
# Coincidentlly, these images have high resolutions. After decreasing it, the problem was solved.
# This method adjust the values of an image to a workable resolution.
# im: 8 or 32 bits image
# Return scaled image
def adjust_resolution(im):
	rows, cols, _ = im.shape

	if rows < 2000 and cols < 1000:
		IO.json_packing_error('ERR_008')
		exit()

	'''
	# But in case that the image has a high resolution, it may hinder the process as well.
    	# If so, we need to lower the resolution.
    	if rows > 3000:
    		ratio = 3 * 10e4 / rows
    		prefsize = int(ratio * cols / 100)

    		im = cv2.resize(im, (prefsize, 3000))
	'''
	return im

# Even this program accepting images both in portrait or landscape orientations
# I decided to fix the portrait as the orientation pattern.
# im: 8 or 32 bits image
# Returns transladed image.
def adjust_position(im):
	rows, cols, _ = im.shape

	if cols > rows:
		im = cv2.transpose(im)
		im = cv2.flip(im, 1)

	return im

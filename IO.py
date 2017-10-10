# -*- coding: utf-8 -*-

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Training.py															  #
# Author: João Herrera		Date: 21 jul, 2017							  #
#																		  #
# Methods for input and output requests									  #
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import json
import numpy as np
from skimage import io, img_as_ubyte


# Open a local database (text) and return its content
# fpath: database path
def open_data(fpath):
	f = open(fpath, 'r')
	data = np.loadtxt(f, delimiter=' ')
	f.close()

	return data

	
# Save data into a text file.
# data: 2D array
# fpath: database path
# mode: overwrite 'w' or append 'a'
def save_data(data, fpath, fmt='%.3f', mode='a'):
	f = open(fpath, mode)
	np.savetxt(f, data, fmt=fmt, delimiter=' ')	
	f.close()


# Show the classification results in an image
# bimage: binary image
# eggs: list of coordinates
# clusters: list of coordinates
def _write_results_on_machine(bimage, eggs, clusters, imname):
	bkimage = img_as_ubyte(np.zeros_like(bimage))
	rows, cols = bkimage.shape

	for egg in eggs:
		for pix in egg['pixels']:
			bkimage[pix[0], pix[1]] = 255

	for cluster in clusters:
		for pix in cluster['pixels']:
			bkimage[pix[0], pix[1]] = 255

	io.imsave("/home/joaoherrera/Desktop/" + imname[:-4] + "_out.jpg", bkimage)



# Result info must be placed according to JSON properties
def json_packing(neggs, imres, version):

	output = {
		'eggs': str(neggs),
		'imresolution': str(imres),
		'ipversion': str(version)
	}

	return json.dumps(output)
# -*- coding: utf-8 -*-

import json
import numpy as np
import os
import IO
import Errors

from skimage import io, img_as_ubyte

IM_RESOLUTION = ''

# initialize some important values. 
# These informations are going to be included in the JSON dictionary for output reasons..
# image: RGB image
def set_outputs(image):
	global IM_RESOLUTION
	
	rows, cols = image.shape[:2] 
	IM_RESOLUTION = str(str(cols) + 'x' + str(rows))



# Open a local database (text) and return its content
# fpath: database path
def open_data(fpath, delimiter=' ', fmt='float'):
	f = open(fpath, 'r')
	data = np.loadtxt(f, delimiter=delimiter, dtype=fmt)
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


# Return dinamically the full path of a file
def get_root(filename):
	return os.path.dirname(os.path.abspath(filename))


# Result info must be placed according to JSON properties
# neggs: number of eggs
# imres: image resolution
def json_packing_success(neggs):

	output = {
        'eggCount': str(neggs),
        'resolution': str(IM_RESOLUTION)
	}

	return json.dumps(output)



# In case an error has been ocurred.
# ercode: error code
# imres: image resolution
# version: current AeIP version
def json_packing_error(errcode):

	# get the error description...
	erdesc = Errors.gen_msg_error(errcode)

	output = {
		'error':{
			'code': str(errcode),
			'message': str(erdesc),
		},
        'resolution': str(IM_RESOLUTION)
	}

	return json.dumps(output)

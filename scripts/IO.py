# -*- coding: utf-8 -*-

import json
import numpy as np
from skimage import io, img_as_ubyte


AEIP_CUR_VERSION = 1.0
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



# Result info must be placed according to JSON properties
# neggs: number of eggs
# imres: image resolution
# version: Current AeIP version
def json_packing_success(neggs):

	output = {
		'eggs': str(neggs),
		'ercode': '',
		'erdesc': '',
		'imresolution': str(IM_RESOLUTION),
		'ipversion': str(AEIP_CUR_VERSION)
	}

	return json.dumps(output)



# In case an error has been ocurred.
# ercode: error code
# imres: image resolution
# version: current AeIP version
def json_packing_error(errcode):

	# get the error description...
	erdesc = get_error_description(errcode)

	output = {
		'eggs': '',
		'ercode': str(errcode),
		'erdesc': str(erdesc),
		'imresolution': str(IM_RESOLUTION),
		'ipversion': str(AEIP_CUR_VERSION)
	}

	return json.dumps(output)



def get_error_description(errcode):
	errors = open_data('Errors.txt', delimiter='$', fmt='str')

	code = errors[:, 0]
	description = errors[:, 1]

	idx = np.where(code == errcode)[0]

	return str(description[idx][0])

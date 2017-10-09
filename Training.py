# -*- coding: utf-8 -*-

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Training.py															  #
# Author: João Herrera		Date: 21 jul, 2017							  #
#																		  #
# These methods are used to extract useful features from the input image  #
# such border lenght, border shape and eggs' colors.					  #
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import numpy as np
import cv2
import IO

from skimage import io


# extract border lenght
# bimage: processed binary image
# objects: border pixels
# radius: radius value
def border_lenght(bimage, objects, radius):
	idx = 1

	for i in range(len(objects)):
		bimage = cv2.putText(img=bimage, text=str(idx), org=(objects[i]['pixels'][0, 1], objects[i]['pixels'][0, 0]), fontFace=3, fontScale=0.3, color=(255), thickness=1)
		IO.save_data(data=np.array([objects[i]['lenght'] / radius, objects[i]['lenght']]).reshape(1, -1), fpath="data/sz.dat", fmt='%.5f')
		idx += 1

	io.imsave("/home/joaoherrera/Desktop/out2.jpg", bimage)


# extract border shape
# bimage: processed binary image
# shapes: minor and major diameters of each object
# radius: radius value
def border_shape(bimage, objects, shapes, filename):
	idx = 1

	for i in range(len(shapes)):
		bimage = cv2.putText(img=bimage, text=str(idx), org=(objects[i]['pixels'][0, 1], objects[i]['pixels'][0, 0]), fontFace=3, fontScale=0.3, color=(255), thickness=1)
		IO.save_data(data=np.array(shapes[i]).reshape(1, -1), fpath="data/"+str(filename), fmt='%.5f', mode='ab')
		idx += 1

	io.imsave("/home/joaoherrera/Desktop/out2.jpg", bimage)


# extract object color
# objects: objects coordinates
# colors: objects colors
def object_color(im, objects, colors, isEgg):
	idx = 1
	path = ""
	imout = ""
	
	if isEgg == True:
		path = "data/cl.dat"
		imout = "egg"
	else:
		path = "data/clcls.dat"
		imout = "cluster"

	for i in range(len(objects)):
		im = cv2.putText(img=im, text=str(idx), org=(objects[i]['pixels'][0, 1], objects[i]['pixels'][0, 0]), fontFace=3, fontScale=0.3, color=(255), thickness=1)
		IO.save_data(data=np.array(colors[i]).reshape(1, -1), fpath=path, fmt='%.5f', mode='ab')
		idx += 1

	io.imsave("/home/joaoherrera/Desktop/"+ imout +".jpg", im)


# extract cluster textures
# clusters: clusters coordinates
# textures: clusters textures
def cluster_texture(im, clusters, textures):
	idx = 1

	for i in range(len(clusters)):
		im = cv2.putText(img=im, text=str(idx), org=(clusters[i]['pixels'][0, 1], clusters[i]['pixels'][0, 0]), fontFace=3, fontScale=0.3, color=(255), thickness=1)
		IO.save_data(data=np.array(textures[i]).reshape(1, -1), fpath="data/tx.dat", fmt='%.0f', mode='ab')
		idx += 1

	io.imsave("/home/joaoherrera/Desktop/out2.jpg", im)
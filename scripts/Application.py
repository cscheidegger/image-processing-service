# -*- coding: utf-8 -*-

import numpy as np
import cv2

from skimage import io, filters, feature, img_as_ubyte, morphology, exposure
from scipy.ndimage.morphology import binary_fill_holes

import Detection as detect
import Utils
import Classification
import Clusterization
import Binary
import types  
import IO
import Defects
import sys


print("Process started")

# image of palette
imname = sys.argv[1]
im = cv2.imread(imname, 1)

# Setting some relevant informations that are going to be returned to server through JSON dictionary...
IO.set_outputs(im)


im = Utils.adjust_position(im)
im = Utils.adjust_resolution(im)


# Check if the palette has a defect. Currently there are 6 implementations of defects analysis:
# low brightness, missing borders, out of focus, shadows and water on the surface. Some of them are detected using deep learning algorithm.
if Defects.isBlurred(im) < 0.1:
	print(IO.json_packing_error('ERR_001'))
	exit()

if Defects.isDark(im) < 110.0:
	print(IO.json_packing_error('ERR_002'))
	exit()


# The first step is to check if the image really has a pallete with a circle at its center.
im = Defects.hasPalette(im)
if type(im) == type(""):
	exit()


print("Detecting circle...")

# detecting the central circle
# The program will try to recognize the central circle in 30 attempts.
# In case the circle isn't yet recognized, we flip the image in 180 degrees.
params = None
for att in range(30):
	params = detect.detect_circle_mark(im)

	if type(params) == type(None):
		
		if att == 29:
			for i in range(2):
				im = cv2.transpose(im)
				im = cv2.flip(im, 1) 

			params = detect.detect_circle_mark(im)

			if type(params) == type(None):
				print(IO.json_packing_error('ERR_003'))
				exit()
			else:
				break

		else:
			continue

	else:
		break



# getting a copy of the original image
imcpy = im.copy()

# crop both original and edited versions to a workable region.
im = Utils.crop_image(im, params)
imcpy = Utils.crop_image(imcpy, params)


# Check if the croped image has shadows or something else that might
# hinder the egg recognition
if Defects.shadow_index(im) > 0.13:
	print(IO.json_packing_error('ERR_004'))
	exit()

# improve contrast among the objects and palette
im = Utils.adjust_contrast(im)

print("\nPerforming segmentation...\n")

# First step: quantization by clusterization to reduce the amount of colors
bimage = Binary.im_threshold(Clusterization.im_quantization(im, 3))



# extracting the features...
# ============================================================== SIZE
# get perimeter of everything is in the image

tinf = [0.10, 0.35]
tsup = [0.10, 0.50]

print("Peforming classification by size...")

# First classification by area. This method aims to classify the objects by its area
# Next, the clusters pixels are going to be labeled by color.
areas_eggs, areas_clusters = Classification.classification_by_area_lenght(detect.object_detection(bimage), params[2], tinf)

# Creating an image containing only clusters.
# Let's label them to separate eggs from ink
clusterim = Binary.bin_from_clusters(areas_clusters, bimage.shape)
clusterim = Clusterization.pix_quantization(im, clusterim)

# Second classification by area... now on the clusters!
# Some clusters might turn to eggs due the clustering process of pixels
new_areas_eggs, areas_clusters = Classification.classification_by_area_lenght(detect.object_detection(clusterim), params[2], tsup)
areas_eggs += new_areas_eggs # adding possible new eggs to the egg list

# Reconstruct binary image.
# After all, let's put these objects into the image
bimage = np.ones_like(bimage, dtype=np.uint8) * 255

for egg in areas_eggs:
	bimage[egg[:, 0], egg[:, 1]] = 0

for cluster in areas_clusters:
	bimage[cluster[:, 0], cluster[:, 1]] = 0

print("Size - Eggs: " + str(len(areas_eggs)))
print("Size - Clusters: " + str(len(areas_clusters)))



# ============================================================== BORDER SHAPE
# checking the shapes of eggs and clusters...

print("\nPerforming shape detection...")

shapes = []
shapes_cls = []

for i in range(len(areas_eggs)):
	shapes.append(detect.shape_detection(detect.get_egg_border(areas_eggs[i], bimage.shape[:2])) / params[2])

for i in range(len(areas_clusters)):
	shapes_cls.append(detect.shape_detection(detect.get_egg_border(areas_clusters[i], bimage.shape[:2])) / params[2])

areas_eggs = Classification.classification_by_ipk(shapes, areas_eggs, "sh.ipk")
areas_clusters = Classification.classification_by_ipk(shapes_cls, areas_clusters, "shcls.ipk")

print("Shape - Eggs: " + str(len(areas_eggs)))
print("Shape - Clusters: " + str(len(areas_clusters)))



# ============================================================== BORDER COLOR
# Classify remaining objects into eggs/cluster or irrelevant spots...
# Unfortunately it doesn't make a sense since there's a huge variability among the samples. 
# However, that's the best option I've found to remove remaining irrelevant objects.

print("\nPerforming color detection...")

imHSV = cv2.cvtColor(imcpy, cv2.COLOR_BGR2HSV)
imLAB = cv2.cvtColor(imcpy, cv2.COLOR_BGR2LAB)

ecolors = detect.get_object_color(areas_eggs, imcpy, imHSV, imLAB)
ccolors = detect.get_object_color(areas_clusters, imcpy, imHSV, imLAB)

areas_eggs = Classification.classification_by_ipk(ecolors, areas_eggs, 'cl.ipk')
areas_clusters = Classification.classification_by_ipk(ccolors, areas_clusters, 'clcls.ipk')

print("Color - Eggs: " + str(len(areas_eggs)))
print("Color - Clusters: " + str(len(areas_clusters)))



# ============================================================== COMPUTATION
# Get the total number of eggs!
# Once the amount of eggs and clusters might be changed, we must to re-calculate their area.
# We use it to compute how many eggs fits in a cluster.

eggs_size_avg = 0
total_eggs = 0

if len(areas_eggs) > 0:	
	total_eggs = len(areas_eggs)

	areas_len = []

	for i in range(len(areas_eggs)):
		areas_len.append(len(areas_eggs[i]))

	eggs_size_avg = np.mean(areas_len)

else:
	eggs_size_avg = params[2] * 0.24  # 0.24 is the ratio of average eggs size by circle radius

# Estimating how many eggs fits in each cluster...
for cluster in areas_clusters:
	total_eggs += np.round(len(cluster) / eggs_size_avg)



print(IO.json_packing_success(int(total_eggs)))
# -*- coding: utf-8 -*-

import numpy as np
import cv2

from skimage import io, filters, feature, img_as_ubyte, morphology, exposure
from scipy.ndimage.morphology import binary_fill_holes

import Detection as detect
import Utils
import Training
import Classification
import types  
import IO
import Defects

AEIP_CUR_VERSION = 1.0


print("Process started")

# image of palette
imname = '36.2SEM.CENC.PERI.SONY.jpg'
im = cv2.imread("/src/samples/" + imname, 1)

im = Utils.adjust_position(im)
im = Utils.adjust_resolution(im)


# image dimensions
rows, cols = im.shape[:2]


# Check if palette has a defect. Currently there are 6 implementations of defects analysis:
# low brightness, missing borders, out of focus, shadows and water on the surface. Some of them are detected using deep learning algorithm.

if Defects.isBlurred(im) < 17.0:
	error = "ERROR: Blurred image!"
	print(error)
	exit()

if Defects.isDark(im) < 130.0:
	error = "ERROR: The image is too dark!"
	print(error)
	exit()


# The first step is to check if the image really has a pallete with a circle at its center.
'''
im = Defects.hasPalette(im)
if type(im) == type(""):
	exit()
'''

print("Detecting circle...\n")

# detecting the central circle
# The program will try to recognize the central circle in 3 attempts.
# In case the circle isn't yet recognized, we stop the execution

params = None
for att in range(3):
	params = detect.detect_circle_mark(im)

	if type(params) == type(None):
		error = "ERROR: Failed to recognize the central circle."
		print(error)

	if att == 2:
		exit()
	else:
		break


# crop image into a feasible region
im = Utils.crop_image(im, params)
gsimage = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)


# Check if the croped image has shadows or something else that might
# hinder the egg recognition
if Defects.shadow_index(im) > 0.13:
	error = "ERROR: The image has shadows or something else that might hinder the egg recognition"
	print(error)
	exit()


print("Performing segmentation...")


# detect borders using canny
cbimage = feature.canny(gsimage, sigma=3)
bimage = morphology.binary_dilation(cbimage)
bimage = img_as_ubyte(bimage) # converting image format to unsigned byte


# extracting the features...
# ============================================================== BORDER SIZE
# get perimeter of everything is in the image

print("Performing border detection...")
objects = detect.object_detection(bimage)

eggs, clusters = Classification.border_lenght_classification(objects, params[2])

#IO._write_results_on_machine(bimage, eggs, clusters, 'out.jpg')



# ============================================================== BORDER SHAPE
# checking the shapes of eggs...

print("Performing shape detection...\n")

shapes = []
for i in range(len(eggs)):
	shapes.append(detect.shape_detection(eggs[i]) / params[2])

shapesc = []
for i in range(len(clusters)):
	shapesc.append(detect.shape_detection(clusters[i]) / params[2])


#Training.border_shape(bimage, eggs, shapes, "sh.dat")
#Training.border_shape(bimage, clusters, shapesc, "shcls.dat")

eggs = Classification.border_shape_classification(shapes, eggs, "sh.dat")
clusters = Classification.border_shape_classification(shapesc, clusters, "shcls.dat")



# ============================================================== BORDER COLOR
# Get colors info of remaining objects...

print("\nPerforming color detection...")

areas_egg = []
areas_clusters = []

imHSV = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
imLAB = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)

for i in range(len(eggs)):
	areas_egg.append(detect.get_object_area(eggs[i], bimage))

for i in range(len(clusters)):
	areas_clusters.append(detect.get_object_area(clusters[i], bimage))


ecolors = detect.get_object_color(areas_egg, im, imHSV, imLAB)
ccolors = detect.get_object_color(areas_clusters, im, imHSV, imLAB)

#Training.object_color(im, eggs, ecolors, True)
#Training.object_color(im, clusters, ccolors, False)

eggs = Classification.object_color_classification(ecolors, eggs, True)
clusters = Classification.object_color_classification(ccolors, clusters, False)

print("Color - Eggs: " + str(len(eggs)))
print("Color - Clusters: " + str(len(clusters)))

# ============================================================== CLUSTER TEXTURE

if len(clusters) > 0:
	cluster_textures = []
	print("\nExtracting cluster textures...")

	imGrey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

	for cluster in areas_clusters:
		cluster_textures.append(detect.get_cluster_texture(cluster, imGrey))

	#Training.cluster_texture(im, clusters, cluster_textures)
	clusters = Classification.cluster_texture_classification(cluster_textures, clusters)



# ============================================================== COMPUTATION
# get the total number of eggs!

eggs_size_avg = 0
total_eggs = 0

if len(eggs) > 0:
	total_eggs = len(eggs)
	for egg in eggs:
		eggs_size_avg += egg['lenght']

	eggs_size_avg /= total_eggs

else:
	eggs_size_avg = 40


for cluster in clusters:
	total_eggs += np.ceil(float(cluster['lenght']) / float(eggs_size_avg))


print(IO.json_packing(int(total_eggs), str(str(cols) + 'x' + str(rows)), AEIP_CUR_VERSION))

#IO._write_results_on_machine(bimage, eggs, clusters, imname)

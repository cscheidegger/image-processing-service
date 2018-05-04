# -*- coding: utf-8 -*-

import numpy as np
import cv2

from skimage import img_as_ubyte


# Segmentation process to remove background
# quant: quantized image
def im_threshold(quant):
    quant = cv2.cvtColor(quant, cv2.COLOR_BGR2LAB)[:,:,0]

    binary = np.ones_like(quant, dtype=np.uint8) * 255
    binary[quant == np.min(quant)] = 0
 
    return img_as_ubyte(binary)


# Create a binary image containing only clusters
# clusters: cluster pixels
# imshape: image shape
def bin_from_clusters(clusters, imshape):
    bim = np.ones(shape=imshape, dtype=np.uint8)

    for cluster in clusters:
        bim[cluster[:, 0], cluster[:, 1]] = 0

    return img_as_ubyte(bim)

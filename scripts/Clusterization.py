# -*- coding: utf-8 -*-

import cv2
import numpy as np
import Classification

from sklearn.cluster import MiniBatchKMeans
from skimage import morphology, img_as_ubyte
from scipy.spatial import distance



# Reduce the amount of colors by performing quantization using K-means technique
# imrgb: rgb image
# clusters: number of clusters
def im_quantization(imrgb, clusters):

    width, height = imrgb.shape[:2]    
    imlab = cv2.cvtColor(imrgb, cv2.COLOR_BGR2LAB)

    # run K-means to clusterize pixels
    clt = MiniBatchKMeans(n_clusters=clusters)
    labels = clt.fit_predict(imlab.reshape(width * height, 3))
    quant = clt.cluster_centers_.astype("uint8")[labels]    

    return cv2.cvtColor(quant.reshape(width, height, 3), cv2.COLOR_LAB2BGR)



# Clusterize objects by color.
# imrgb: rgb image
# imquant: binary image containing clusters and irrelevant spots.
def pix_quantization(imrgb, imquant):
    imlab = cv2.cvtColor(imrgb, cv2.COLOR_BGR2LAB)
    ihsv = imlab[imquant == 0]

    # run K-means to clusterize pixels
    clt = MiniBatchKMeans(n_clusters=5)
    labels = clt.fit_predict(ihsv.reshape(-1, 3))
    quant = clt.cluster_centers_.astype("uint8")[labels]

    # turning a LAB image into a white RGB image
    imlab = np.ones_like(imlab, dtype=np.uint8)
    imlab[:,:,0] = 255
    imlab[:,:,1] = 128
    imlab[:,:,2] = 128

    # fill the blank image with clusterized pixels
    imlab[imquant == 0] = quant
    srgb = cv2.cvtColor(imlab, cv2.COLOR_LAB2BGR)

    clusters = np.unique(srgb.reshape(-1, 3), axis=0)[:2]

    # finding the darkest cluster center. This color will determine the eggs' cluster
    nwhite = 255
    icluster = 0
    for i in range(len(clusters)):
        diff = clusters[i][0]# - np.mean(clusters[i])

        if diff > 0 and diff < nwhite:
            nwhite = diff
            icluster = i

    srgb[srgb == clusters[icluster]] = 0
    srgb[srgb > (0, 0, 0)] = 255

    # Restoring some pixels lost during the clustering process.
    imbin = morphology.closing(cv2.cvtColor(srgb, cv2.COLOR_BGR2GRAY))
    imbin = cv2.erode(imbin, np.ones((5,5), dtype=np.uint8))

    return img_as_ubyte(imbin)

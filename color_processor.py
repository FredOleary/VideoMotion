import time
import cv2
import numpy as np


class ColorProcessor:
    """ColorProcessor calculates average colors in ROI"""

    @staticmethod
    def get_average_color( dimension, source_image, rectROI):
        # rectROI is organized as (pos_left, pos_top, width, height, (x,y,w,h)
        # If (x1,y1) and (x2,y2) are the two opposite vertices of mat
        # roi_filtered = source_image[y1:y2, x1:x2]
        # NOTE OpenCV uses BGR, NOT RGB
        roi_filtered = source_image[rectROI[1]:rectROI[1]+rectROI[3], rectROI[0]:rectROI[0]+rectROI[2]]
        color_average = 0;

        if dimension == 'R':
            # set blue and green channels to 0
            roi_filtered[:, :, 0] = 0
            roi_filtered[:, :, 1] = 0
            avg_color_per_row = np.average(roi_filtered, axis=0)
            color_average = np.average(avg_color_per_row, axis=0)[2]
        elif dimension == 'B':
            # set green and red channels to 0
            roi_filtered[:, :, 1] = 0
            roi_filtered[:, :, 2] = 0
            avg_color_per_row = np.average(roi_filtered, axis=0)
            color_average = np.average(avg_color_per_row, axis=0)[0]
        else:
            # set blue and red channels to 0
            roi_filtered[:, :, 0] = 0
            roi_filtered[:, :, 2] = 0
            avg_color_per_row = np.average(roi_filtered, axis=0)
            color_average = np.average(avg_color_per_row, axis=0)[1]


        return color_average, roi_filtered

import cv2
import numpy as np


class Services:
    @staticmethod
    def filter_image(image, filter_type):
        if filter_type == 'grayscale':
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif filter_type == 'blur':
            return cv2.blur(image, (5, 5))
        elif filter_type == 'median':
            return cv2.medianBlur(image, 5)
        else:
            return image

    @staticmethod
    def smooth_image(image, smoothing_type):
        if smoothing_type == 'gaussian':
            return cv2.GaussianBlur(image, (5, 5), 0)
        elif smoothing_type == 'bilateral':
            return cv2.bilateralFilter(image, 9, 75, 75)
        else:
            return image

    @staticmethod
    def sharpen_image(image, sharpening_type):
        if sharpening_type == 'unsharp_mask':
            gaussian = cv2.GaussianBlur(image, (9, 9), 10.0)
            return cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        elif sharpening_type == 'laplacian':
            return cv2.Laplacian(image, cv2.CV_64F)
        else:
            return image

    @staticmethod
    def invert_colors(image):
        return cv2.bitwise_not(image)

    @staticmethod
    def contrast_stretching(image):
        hist, bins = np.histogram(image.flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf_m = np.ma.masked_equal(cdf, 0)
        cdf_m = (cdf_m - cdf_m.min()) * 255 / (cdf_m.max() - cdf_m.min())
        cdf = np.ma.filled(cdf_m, 0).astype('uint8')
        return cdf[image]

    @staticmethod
    def brightening(image, alpha=1.5, beta=30):
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    @staticmethod
    def darkening(image, alpha=0.5, beta=30):
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    @classmethod
    def edge_detection(cls, img):

        blurred_image = cv2.GaussianBlur(img, (5, 5), 0)
        edges = cv2.Canny(blurred_image, 50, 150)
        return edges

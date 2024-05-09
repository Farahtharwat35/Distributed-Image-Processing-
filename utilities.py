import cv2
import numpy as np


class Utilities:
    @staticmethod
    def invert(image):
        return cv2.bitwise_not(image)

    @staticmethod
    def saturate(image, value):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] += value
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    @staticmethod
    def rgb_to_gray(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def gray_to_rgb(image):
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def fourier_transform(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply Fourier Transform
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        return fshift

    @staticmethod
    def butterworth_lowpass_filter(image, cutoff_frequency, order):
        rows, cols = image.shape
        crow, ccol = int(rows / 2), int(cols / 2)
        x = np.linspace(-0.5, 0.5, cols) * cols
        y = np.linspace(-0.5, 0.5, rows) * rows
        X, Y = np.meshgrid(x, y)
        radius = np.sqrt((X - ccol) ** 2 + (Y - crow) ** 2)
        filter_array = 1 / (1.0 + (radius / cutoff_frequency) ** (2 * order))
        return filter_array

    @staticmethod
    def apply_lowpass_filter(image, cutoff_frequency, order):
        fshift = Utilities.fourier_transform(image)
        low_pass_filter = Utilities.butterworth_lowpass_filter(image, cutoff_frequency, order)
        # Apply filter to Fourier Transform of the image
        filtered_image = fshift * low_pass_filter
        # Apply inverse Fourier Transform
        img_back = np.fft.ifftshift(filtered_image)
        img_back = np.fft.ifft2(img_back)
        img_back = np.abs(img_back)
        return img_back

    @staticmethod
    def butterworth_highpass_filter(image, cutoff_frequency, order):
        return 1 - Utilities.butterworth_lowpass_filter(image, cutoff_frequency, order)

    @staticmethod
    def apply_highpass_filter(image, cutoff_frequency, order):
        fshift = Utilities.fourier_transform(image)
        high_pass_filter = Utilities.butterworth_highpass_filter(image, cutoff_frequency, order)
        # Apply filter to Fourier Transform of the image
        filtered_image = fshift * high_pass_filter
        # Apply inverse Fourier Transform
        img_back = np.fft.ifftshift(filtered_image)
        img_back = np.fft.ifft2(img_back)
        img_back = np.abs(img_back)
        return img_back

    @staticmethod
    def blur_image(image, kernel_size):
        return cv2.blur(image, (kernel_size, kernel_size))

    @staticmethod
    def sharpen_image(image):
        kernel = np.array([[0,1,0], [1,-4,1], [0,1,0]])
        return cv2.filter2D(image, -1, kernel)

    @staticmethod
    def remove_gaussian_noise(image, kernel_size):
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    @staticmethod
    def remove_salt_pepper_noise(image, kernel_size):
        return cv2.medianBlur(image, kernel_size)

    @staticmethod
    def sobel_filter(image, kernel_size):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=kernel_size)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=kernel_size)
        return np.hypot(sobelx, sobely)

    @staticmethod
    def prewitt_filter(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        img_prewittx = cv2.filter2D(gray, -1, kernelx)
        img_prewitty = cv2.filter2D(gray, -1, kernely)
        return np.hypot(img_prewittx, img_prewitty)

    @staticmethod
    def roberts_filter(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernelx = np.array([[1, 0], [0, -1]])
        kernely = np.array([[0, 1], [-1, 0]])
        img_robertsx = cv2.filter2D(gray, -1, kernelx)
        img_robertsy = cv2.filter2D(gray, -1, kernely)
        return np.hypot(img_robertsx, img_robertsy)

    @staticmethod
    def canny_edge_filter(image, threshold1, threshold2):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(gray, threshold1, threshold2)

    @staticmethod
    def hough_transform(image, rho, theta, threshold):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, rho, theta, threshold)
        return lines

    @staticmethod
    def harris_corner_detection(image, blockSize, ksize, k):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners = cv2.cornerHarris(gray, blockSize, ksize, k)
        return corners

    @staticmethod
    def binary_threshold(image, threshold_value):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        return thresh

    @staticmethod
    def otsu_threshold(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return thresh

    @staticmethod
    def gaussian_threshold(image, threshold_value):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        ret, thresh = cv2.threshold(blur, threshold_value, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return thresh

    @staticmethod
    def mean_adaptive_threshold(image, block_size, constant):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, constant)
        return thresh

    @staticmethod
    def gaussian_adaptive_threshold(image, block_size, constant):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, constant)
        return thresh

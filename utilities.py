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
        # In butterworth_lowpass_filter function
        if len(image.shape) == 2:
            rows, cols = image.shape
        elif len(image.shape) == 3:
            rows, cols, channels = image.shape
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
        # Create a copy of the original image to draw lines on
        image_with_lines = np.copy(image)
        
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Perform edge detection using the Canny edge detector
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Apply the Hough Transform to detect lines
        lines = cv2.HoughLines(edges, rho, theta, threshold)
        
        # Draw detected lines on the image copy
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(image_with_lines, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        return image_with_lines
    
    # @staticmethod
    # def harris_corner_detection(image, blockSize, ksize, k):
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     corners = cv2.cornerHarris(gray, blockSize, ksize, k)
    #     return corners
    def harris_corner_detection(image, blockSize=2, ksize=3, k=0.04):
        # Converting the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Applying Harris corner detection
        corners = cv2.cornerHarris(gray, blockSize, ksize, k)
        
        # Threshold for an optimal value, it may vary depending on the image.
        corners = cv2.dilate(corners, None)
        
        # Creating an RGB image with corner markers
        output_image = np.copy(image)
        output_image[corners > 0.01 * corners.max()] = [0, 0, 255]  # Marking corners in red
        return output_image
    
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

    # @staticmethod
    # def mean_adaptive_threshold(image, block_size, constant):
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, constant)
    #     return thresh
    def mean_adaptive_threshold(image, block_size=11, constant=2):
        """
        Apply mean adaptive thresholding to an image.

        Parameters:
        - image: The input image (numpy array).
        - block_size: Size of the pixel neighborhood used to calculate the threshold value. Must be odd and greater than 1.
        - constant: A constant value that is subtracted from the mean or weighted mean.

        Returns:
        - thresholded_image: The thresholded image (same number of channels as input).
        """
        # Ensuring block_size is odd and greater than 1
        if block_size % 2 == 0 or block_size <= 1:
            raise ValueError("block_size must be an odd number and greater than 1.")

        # Converting to grayscale if the image has more than one channel
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Applying adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 
            255, 
            cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, 
            block_size, 
            constant
        )

        # Converting back to 3 channels if the original image had 3 channels
        if len(image.shape) == 3 and image.shape[2] == 3:
            thresholded_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        else:
            thresholded_image = thresh

        return thresholded_image

    @staticmethod
    def gaussian_adaptive_threshold(image, block_size, constant):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, constant)
        return thresh

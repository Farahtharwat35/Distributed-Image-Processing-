import threading
from utilities import Services


class WorkerThread(threading.Thread):
    def __init__(self, service_num, img):
        threading.Thread.__init__(self)
        self.service_num = service_num
        self.img = img

    def run(self):
        self.result = self.process_image(self.service_num, self.img)

    def process_image(self, service_num, img):

        if service_num == 1:
            result = Services.filter_image(img, 'grayscale')
        elif service_num == 2:
            result = Services.filter_image(img, 'blur')
        elif service_num == 3:
            result = Services.filter_image(img, 'median')
        elif service_num == 4:
            result = Services.smooth_image(img, 'gaussian')
        elif service_num == 5:
            result = Services.smooth_image(img, 'bilateral')
        elif service_num == 6:
            result = Services.sharpen_image(img, 'unsharp_mask')
        elif service_num == 7:
            result = Services.sharpen_image(img, 'laplacian')
        elif service_num == 8:
            result = Services.invert_colors(img)
        elif service_num == 9:
            result = Services.contrast_stretching(img)
        elif service_num == 10:
            result = Services.brightening(img)
        elif service_num == 11:
            result = Services.darkening(img)
        elif service_num == 12:
            result = Services.edge_detection(img)

        return result